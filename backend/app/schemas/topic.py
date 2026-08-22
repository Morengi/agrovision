import uuid

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.content_item import ContentItemSummary


class TopicRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    course_id: uuid.UUID
    title: str
    description: str
    order_index: int


class TopicWithItems(TopicRead):
    content_items: list[ContentItemSummary]


class TopicCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: str = ""
    order_index: int | None = None


class TopicUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    order_index: int | None = None
