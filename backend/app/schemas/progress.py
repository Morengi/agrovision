import uuid
from decimal import Decimal

from pydantic import BaseModel


class TopicProgressSummary(BaseModel):
    topic_id: uuid.UUID
    title: str
    total_items: int
    completed_items: int


class CourseProgressSummary(BaseModel):
    course_id: uuid.UUID
    title: str
    slug: str
    cover_image_path: str | None
    price: Decimal
    total_items: int
    completed_items: int
    percent: int
    topics: list[TopicProgressSummary]


class DashboardResponse(BaseModel):
    courses: list[CourseProgressSummary]
