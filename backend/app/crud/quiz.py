import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.quiz import QuizOption, QuizQuestion


async def get_question_by_id(db: AsyncSession, question_id: uuid.UUID) -> QuizQuestion | None:
    stmt = select(QuizQuestion).where(QuizQuestion.id == question_id).options(selectinload(QuizQuestion.options))
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def list_questions_by_content_item(db: AsyncSession, content_item_id: uuid.UUID) -> list[QuizQuestion]:
    stmt = (
        select(QuizQuestion)
        .where(QuizQuestion.content_item_id == content_item_id)
        .order_by(QuizQuestion.order_index)
        .options(selectinload(QuizQuestion.options))
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def next_question_order_index(db: AsyncSession, content_item_id: uuid.UUID) -> int:
    result = await db.execute(
        select(func.coalesce(func.max(QuizQuestion.order_index), -1)).where(
            QuizQuestion.content_item_id == content_item_id
        )
    )
    return result.scalar_one() + 1


async def create_question(
    db: AsyncSession,
    *,
    content_item_id: uuid.UUID,
    question_text: str,
    allow_multiple: bool,
    order_index: int | None,
) -> QuizQuestion:
    if order_index is None:
        order_index = await next_question_order_index(db, content_item_id)

    question = QuizQuestion(
        content_item_id=content_item_id,
        question_text=question_text,
        allow_multiple=allow_multiple,
        order_index=order_index,
    )
    db.add(question)
    await db.commit()
    await db.refresh(question)
    return await get_question_by_id(db, question.id)


async def update_question(
    db: AsyncSession,
    question: QuizQuestion,
    *,
    question_text: str | None = None,
    allow_multiple: bool | None = None,
    order_index: int | None = None,
) -> QuizQuestion:
    if question_text is not None:
        question.question_text = question_text
    if allow_multiple is not None:
        question.allow_multiple = allow_multiple
    if order_index is not None:
        question.order_index = order_index

    await db.commit()
    await db.refresh(question)
    return question


async def delete_question(db: AsyncSession, question: QuizQuestion) -> None:
    await db.delete(question)
    await db.commit()


async def get_option_by_id(db: AsyncSession, option_id: uuid.UUID) -> QuizOption | None:
    return await db.get(QuizOption, option_id)


async def next_option_order_index(db: AsyncSession, question_id: uuid.UUID) -> int:
    result = await db.execute(
        select(func.coalesce(func.max(QuizOption.order_index), -1)).where(QuizOption.question_id == question_id)
    )
    return result.scalar_one() + 1


async def create_option(
    db: AsyncSession, *, question_id: uuid.UUID, text: str, is_correct: bool, order_index: int | None
) -> QuizOption:
    if order_index is None:
        order_index = await next_option_order_index(db, question_id)

    option = QuizOption(question_id=question_id, text=text, is_correct=is_correct, order_index=order_index)
    db.add(option)
    await db.commit()
    await db.refresh(option)
    return option


async def update_option(
    db: AsyncSession,
    option: QuizOption,
    *,
    text: str | None = None,
    is_correct: bool | None = None,
    order_index: int | None = None,
) -> QuizOption:
    if text is not None:
        option.text = text
    if is_correct is not None:
        option.is_correct = is_correct
    if order_index is not None:
        option.order_index = order_index

    await db.commit()
    await db.refresh(option)
    return option


async def delete_option(db: AsyncSession, option: QuizOption) -> None:
    await db.delete(option)
    await db.commit()
