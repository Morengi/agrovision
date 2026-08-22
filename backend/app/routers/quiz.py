import uuid
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import require_enrollment, require_role
from app.crud import attempt as attempt_crud
from app.crud import progress as progress_crud
from app.crud import quiz as quiz_crud
from app.db.session import get_db
from app.models.user import User, UserRole
from app.schemas.quiz import (
    QuizOptionAdmin,
    QuizOptionCreate,
    QuizOptionUpdate,
    QuizQuestionAdmin,
    QuizQuestionCreate,
    QuizQuestionResult,
    QuizQuestionUpdate,
    QuizSubmitRequest,
    QuizSubmitResult,
)

router = APIRouter(tags=["quiz"])


@router.post(
    "/content-items/{item_id}/quiz-questions", response_model=QuizQuestionAdmin, status_code=status.HTTP_201_CREATED
)
async def create_quiz_question(
    item_id: uuid.UUID,
    payload: QuizQuestionCreate,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_role(UserRole.moderator, UserRole.admin)),
):
    question = await quiz_crud.create_question(
        db,
        content_item_id=item_id,
        question_text=payload.question_text,
        allow_multiple=payload.allow_multiple,
        order_index=payload.order_index,
    )
    return QuizQuestionAdmin.model_validate(question)


@router.patch("/quiz-questions/{question_id}", response_model=QuizQuestionAdmin)
async def update_quiz_question(
    question_id: uuid.UUID,
    payload: QuizQuestionUpdate,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_role(UserRole.moderator, UserRole.admin)),
):
    question = await quiz_crud.get_question_by_id(db, question_id)
    if question is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Вопрос не найден")

    question = await quiz_crud.update_question(
        db,
        question,
        question_text=payload.question_text,
        allow_multiple=payload.allow_multiple,
        order_index=payload.order_index,
    )
    return QuizQuestionAdmin.model_validate(question)


@router.delete("/quiz-questions/{question_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_quiz_question(
    question_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_role(UserRole.moderator, UserRole.admin)),
):
    question = await quiz_crud.get_question_by_id(db, question_id)
    if question is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Вопрос не найден")
    await quiz_crud.delete_question(db, question)


@router.post(
    "/quiz-questions/{question_id}/options", response_model=QuizOptionAdmin, status_code=status.HTTP_201_CREATED
)
async def create_quiz_option(
    question_id: uuid.UUID,
    payload: QuizOptionCreate,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_role(UserRole.moderator, UserRole.admin)),
):
    option = await quiz_crud.create_option(
        db, question_id=question_id, text=payload.text, is_correct=payload.is_correct, order_index=payload.order_index
    )
    return QuizOptionAdmin.model_validate(option)


@router.patch("/quiz-options/{option_id}", response_model=QuizOptionAdmin)
async def update_quiz_option(
    option_id: uuid.UUID,
    payload: QuizOptionUpdate,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_role(UserRole.moderator, UserRole.admin)),
):
    option = await quiz_crud.get_option_by_id(db, option_id)
    if option is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Вариант не найден")

    option = await quiz_crud.update_option(
        db, option, text=payload.text, is_correct=payload.is_correct, order_index=payload.order_index
    )
    return QuizOptionAdmin.model_validate(option)


@router.delete("/quiz-options/{option_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_quiz_option(
    option_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_role(UserRole.moderator, UserRole.admin)),
):
    option = await quiz_crud.get_option_by_id(db, option_id)
    if option is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Вариант не найден")
    await quiz_crud.delete_option(db, option)


@router.post("/content-items/{item_id}/quiz/submit", response_model=QuizSubmitResult)
async def submit_quiz(
    item_id: uuid.UUID,
    payload: QuizSubmitRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_enrollment),
):
    questions = await quiz_crud.list_questions_by_content_item(db, item_id)
    if not questions:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Тест не найден")

    answers_by_question = {a.question_id: set(a.selected_option_ids) for a in payload.answers}

    results: list[QuizQuestionResult] = []
    attempt_answers: list[dict] = []
    correct_count = 0

    for question in questions:
        correct_option_ids = {o.id for o in question.options if o.is_correct}
        selected_ids = answers_by_question.get(question.id, set())
        is_correct = selected_ids == correct_option_ids

        if is_correct:
            correct_count += 1

        results.append(
            QuizQuestionResult(
                question_id=question.id,
                is_correct=is_correct,
                correct_option_ids=list(correct_option_ids),
                selected_option_ids=list(selected_ids),
            )
        )
        attempt_answers.append(
            {"question_id": question.id, "selected_option_ids": list(selected_ids), "is_correct": is_correct}
        )

    total_count = len(questions)
    score_percent = Decimal(correct_count) / Decimal(total_count) * 100 if total_count else Decimal(0)
    passed = correct_count == total_count

    await attempt_crud.record_quiz_attempt(
        db,
        user_id=user.id,
        content_item_id=item_id,
        score_percent=score_percent.quantize(Decimal("0.01")),
        correct_count=correct_count,
        total_count=total_count,
        passed=passed,
        answers=attempt_answers,
    )
    await progress_crud.mark_completed(db, user_id=user.id, content_item_id=item_id)

    return QuizSubmitResult(
        score_percent=float(score_percent),
        correct_count=correct_count,
        total_count=total_count,
        passed=passed,
        questions=results,
    )
