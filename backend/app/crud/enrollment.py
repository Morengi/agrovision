import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enrollment import Enrollment, PaymentStatus


async def get_enrollment(db: AsyncSession, *, user_id: uuid.UUID, course_id: uuid.UUID) -> Enrollment | None:
    result = await db.execute(
        select(Enrollment).where(Enrollment.user_id == user_id, Enrollment.course_id == course_id)
    )
    return result.scalar_one_or_none()


async def list_enrollments_for_user(db: AsyncSession, user_id: uuid.UUID) -> list[Enrollment]:
    result = await db.execute(select(Enrollment).where(Enrollment.user_id == user_id))
    return list(result.scalars().all())


async def create_enrollment(
    db: AsyncSession, *, user_id: uuid.UUID, course_id: uuid.UUID, payment_status: PaymentStatus
) -> Enrollment:
    enrollment = Enrollment(user_id=user_id, course_id=course_id, payment_status=payment_status)
    db.add(enrollment)
    await db.commit()
    await db.refresh(enrollment)
    return enrollment
