import uuid

from pydantic import BaseModel, ConfigDict, Field

from app.models.content_item import ContentItemType
from app.schemas.photocase import PhotocaseOptionAdmin, PhotocaseOptionPublic
from app.schemas.quiz import QuizQuestionAdmin, QuizQuestionPublic


class ContentItemImageRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    image_path: str
    caption: str
    order_index: int


class ContentItemSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    topic_id: uuid.UUID
    type: ContentItemType
    title: str
    order_index: int


class ContentItemDetail(ContentItemSummary):
    """Student-facing view — never exposes which answer is correct."""

    text_body: str | None
    images: list[ContentItemImageRead]
    photocase_options: list[PhotocaseOptionPublic] = []
    quiz_questions: list[QuizQuestionPublic] = []


class ContentItemAdminDetail(ContentItemSummary):
    """Moderator/admin authoring view — includes answers and breakdown fields."""

    text_body: str | None
    key_signs: str | None
    next_steps: str | None
    images: list[ContentItemImageRead]
    photocase_options: list[PhotocaseOptionAdmin] = []
    quiz_questions: list[QuizQuestionAdmin] = []


class ContentItemCreate(BaseModel):
    type: ContentItemType
    title: str = Field(min_length=1, max_length=255)
    order_index: int | None = None
    text_body: str | None = None


class ContentItemUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    order_index: int | None = None
    text_body: str | None = None
    key_signs: str | None = None
    next_steps: str | None = None
