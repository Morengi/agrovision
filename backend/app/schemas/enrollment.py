import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.enrollment import PaymentStatus


class EnrollmentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    course_id: uuid.UUID
    payment_status: PaymentStatus
    purchased_at: datetime
