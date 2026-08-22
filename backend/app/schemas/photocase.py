import uuid

from pydantic import BaseModel, ConfigDict, Field


class PhotocaseOptionPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    label: str


class PhotocaseOptionAdmin(PhotocaseOptionPublic):
    is_correct: bool
    explanation: str
    order_index: int


class PhotocaseOptionCreate(BaseModel):
    label: str = Field(min_length=1, max_length=255)
    is_correct: bool = False
    explanation: str = ""
    order_index: int | None = None


class PhotocaseOptionUpdate(BaseModel):
    label: str | None = Field(default=None, min_length=1, max_length=255)
    is_correct: bool | None = None
    explanation: str | None = None
    order_index: int | None = None


class PhotocaseSubmitRequest(BaseModel):
    selected_option_id: uuid.UUID


class PhotocaseSubmitResult(BaseModel):
    is_correct: bool
    selected_option_id: uuid.UUID
    key_signs: str | None
    next_steps: str | None
    options: list[PhotocaseOptionAdmin]
