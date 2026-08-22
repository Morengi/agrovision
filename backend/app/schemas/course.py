import uuid
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.tag import TagRead
from app.schemas.topic import TopicWithItems


class CourseListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    slug: str
    description: str
    cover_image_path: str | None
    price: Decimal
    is_published: bool
    tags: list[TagRead]


class CourseDetail(CourseListItem):
    topics: list[TopicWithItems]


class CourseCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: str = ""
    price: Decimal = Decimal("0")
    tag_ids: list[uuid.UUID] = []


class CourseUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    price: Decimal | None = None
    is_published: bool | None = None
    tag_ids: list[uuid.UUID] | None = None


class PaginatedCourses(BaseModel):
    items: list[CourseListItem]
    total: int
    page: int
    page_size: int
