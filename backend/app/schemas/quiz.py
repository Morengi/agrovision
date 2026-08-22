import uuid

from pydantic import BaseModel, ConfigDict, Field


class QuizOptionPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    text: str


class QuizOptionAdmin(QuizOptionPublic):
    is_correct: bool
    order_index: int


class QuizOptionCreate(BaseModel):
    text: str = Field(min_length=1, max_length=500)
    is_correct: bool = False
    order_index: int | None = None


class QuizOptionUpdate(BaseModel):
    text: str | None = Field(default=None, min_length=1, max_length=500)
    is_correct: bool | None = None
    order_index: int | None = None


class QuizQuestionPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    question_text: str
    allow_multiple: bool
    order_index: int
    options: list[QuizOptionPublic]


class QuizQuestionAdmin(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    question_text: str
    allow_multiple: bool
    order_index: int
    options: list[QuizOptionAdmin]


class QuizQuestionCreate(BaseModel):
    question_text: str = Field(min_length=1)
    allow_multiple: bool = False
    order_index: int | None = None


class QuizQuestionUpdate(BaseModel):
    question_text: str | None = Field(default=None, min_length=1)
    allow_multiple: bool | None = None
    order_index: int | None = None


class QuizAnswerSubmit(BaseModel):
    question_id: uuid.UUID
    selected_option_ids: list[uuid.UUID]


class QuizSubmitRequest(BaseModel):
    answers: list[QuizAnswerSubmit]


class QuizQuestionResult(BaseModel):
    question_id: uuid.UUID
    is_correct: bool
    correct_option_ids: list[uuid.UUID]
    selected_option_ids: list[uuid.UUID]


class QuizSubmitResult(BaseModel):
    score_percent: float
    correct_count: int
    total_count: int
    passed: bool
    questions: list[QuizQuestionResult]
