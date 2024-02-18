from __future__ import annotations

from typing import TYPE_CHECKING, Final
from uuid import UUID

import sqlalchemy as sa
from litestar.contrib.sqlalchemy.base import UUIDBase
from pydantic import BaseModel as _BaseModel
from sqlalchemy.orm import Mapped, relationship


class BaseModel(_BaseModel):
    """Extend Pydantic's BaseModel to enable ORM mode"""

    model_config = {"from_attributes": True}


class NoteModel(UUIDBase):
    # we can optionally provide the table name instead of auto-generating it
    __tablename__ = "note"  # type: ignore[assignment]
    title: Mapped[str]
    tags: Mapped[list[TagModel]] = relationship(
        secondary=lambda: note_tag,
        back_populates="notes",
        cascade="all, delete",
        passive_deletes=True,
        lazy="selectin",
    )


class TagModel(UUIDBase):
    __tablename__ = "tag"
    title: Mapped[str]
    notes: Mapped[list[NoteModel]] = relationship(
        secondary=lambda: note_tag,
        back_populates="tags",
        lazy="selectin",
    )


note_tag: Final[sa.Table] = sa.Table(
    "note_tag",
    UUIDBase.metadata,
    sa.Column("note_id", sa.ForeignKey("note.id", ondelete="CASCADE"), primary_key=True),
    sa.Column("tag_id", sa.ForeignKey("tag.id", ondelete="CASCADE"), primary_key=True),
)


# we will explicitly define the schema instead of using DTO objects for clarity.

class Tag(BaseModel):
    title: str


class Note(BaseModel):
    id: UUID | None
    title: str
    tags: list[Tag]


class NoteCreate(BaseModel):
    title: str


class NoteUpdate(BaseModel):
    title: str | None = None
