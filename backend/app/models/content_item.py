import enum
import uuid

from sqlalchemy import Enum, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class ContentItemType(str, enum.Enum):
    text_lecture = "text_lecture"
    quiz = "quiz"
    photocase = "photocase"


class ContentItem(Base):
    __tablename__ = "content_items"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    topic_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("topics.id", ondelete="CASCADE"), nullable=False, index=True
    )
    type: Mapped[ContentItemType] = mapped_column(Enum(ContentItemType, name="content_item_type"), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    order_index: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # text_lecture
    text_body: Mapped[str | None] = mapped_column(Text, nullable=True)

    # photocase — shown in the breakdown after the student answers
    key_signs: Mapped[str | None] = mapped_column(Text, nullable=True)
    next_steps: Mapped[str | None] = mapped_column(Text, nullable=True)

    images: Mapped[list["ContentItemImage"]] = relationship(  # noqa: F821
        back_populates="content_item", order_by="ContentItemImage.order_index", cascade="all, delete-orphan"
    )
    photocase_options: Mapped[list["PhotocaseOption"]] = relationship(  # noqa: F821
        order_by="PhotocaseOption.order_index", cascade="all, delete-orphan"
    )
    quiz_questions: Mapped[list["QuizQuestion"]] = relationship(  # noqa: F821
        order_by="QuizQuestion.order_index", cascade="all, delete-orphan"
    )
