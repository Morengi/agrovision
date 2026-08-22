import uuid
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.attempt import PhotocaseAttempt, QuizAttempt, QuizAttemptAnswer


async def record_photocase_attempt(
    db: AsyncSession, *, user_id: uuid.UUID, content_item_id: uuid.UUID, selected_option_id: uuid.UUID, is_correct: bool
) -> PhotocaseAttempt:
    attempt = PhotocaseAttempt(
        user_id=user_id,
        content_item_id=content_item_id,
        selected_option_id=selected_option_id,
        is_correct=is_correct,
    )
    db.add(attempt)
    await db.commit()
    await db.refresh(attempt)
    return attempt


async def record_quiz_attempt(
    db: AsyncSession,
    *,
    user_id: uuid.UUID,
    content_item_id: uuid.UUID,
    score_percent: Decimal,
    correct_count: int,
    total_count: int,
    passed: bool,
    answers: list[dict],
) -> QuizAttempt:
    attempt = QuizAttempt(
        user_id=user_id,
        content_item_id=content_item_id,
        score_percent=score_percent,
        correct_count=correct_count,
        total_count=total_count,
        passed=passed,
    )
    db.add(attempt)
    await db.flush()

    for answer in answers:
        db.add(
            QuizAttemptAnswer(
                attempt_id=attempt.id,
                question_id=answer["question_id"],
                selected_option_ids=[str(i) for i in answer["selected_option_ids"]],
                is_correct=answer["is_correct"],
            )
        )

    await db.commit()
    return attempt
