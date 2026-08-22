import uuid
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user
from app.crud import course as course_crud
from app.crud import enrollment as enrollment_crud
from app.db.session import get_db
from app.models.enrollment import PaymentStatus
from app.models.user import User
from app.schemas.enrollment import EnrollmentRead

router = APIRouter(tags=["enrollments"])


@router.post("/courses/{course_id}/enroll", response_model=EnrollmentRead, status_code=status.HTTP_201_CREATED)
async def enroll_in_course(
    course_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    course = await course_crud.get_by_id(db, course_id)
    if course is None or not course.is_published:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Курс не найден")

    existing = await enrollment_crud.get_enrollment(db, user_id=user.id, course_id=course_id)
    if existing is not None:
        return EnrollmentRead.model_validate(existing)

    if course.price == Decimal("0"):
        payment_status = PaymentStatus.free
    else:
        # TODO: integrate a real payment gateway (e.g. YooKassa) here before marking
        # the enrollment as paid. For now this is a stub: any paid course is granted
        # immediately without collecting payment.
        payment_status = PaymentStatus.stub_paid

    enrollment = await enrollment_crud.create_enrollment(
        db, user_id=user.id, course_id=course_id, payment_status=payment_status
    )
    return EnrollmentRead.model_validate(enrollment)


@router.get("/users/me/enrollments", response_model=list[EnrollmentRead])
async def list_my_enrollments(db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    enrollments = await enrollment_crud.list_enrollments_for_user(db, user.id)
    return [EnrollmentRead.model_validate(e) for e in enrollments]
