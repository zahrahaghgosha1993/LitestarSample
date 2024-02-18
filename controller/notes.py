from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from advanced_alchemy import SQLAlchemyAsyncRepository
from litestar import get
from litestar.controller import Controller
from litestar.di import Provide
from litestar.handlers.http_handlers.decorators import delete, patch, post
from litestar.pagination import OffsetPagination
from litestar.params import Parameter
from litestar.repository.filters import LimitOffset
from pydantic import TypeAdapter
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from domain.notes import NoteModel, Note, NoteUpdate, NoteCreate

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


class NoteRepository(SQLAlchemyAsyncRepository[NoteModel]):
    """Note repository."""

    model_type = NoteModel


async def provide_notes_repo(db_session: AsyncSession) -> NoteRepository:
    """This provides the default Notes repository."""
    return NoteRepository(session=db_session)


async def provide_note_details_repo(db_session: AsyncSession) -> NoteRepository:
    """This provides a simple example demonstrating how to override the join options for the repository."""
    return NoteRepository(
        statement=select(NoteModel).options(selectinload(NoteModel.tags)),
        session=db_session,
    )


class NoteController(Controller):
    """Note CRUD"""

    dependencies = {"notes_repo": Provide(provide_notes_repo)}

    @get(path="/notes")
    async def list_notes(
            self,
            notes_repo: NoteRepository,
            limit_offset: LimitOffset,
    ) -> OffsetPagination[Note]:
        """List notes."""
        results, total = await notes_repo.list_and_count(limit_offset)
        type_adapter = TypeAdapter(list[Note])
        return OffsetPagination[Note](
            items=type_adapter.validate_python(results),
            total=total,
            limit=limit_offset.limit,
            offset=limit_offset.offset,
        )

    @post(path="/notes")
    async def create_note(
            self,
            notes_repo: NoteRepository,
            data: NoteCreate,
    ) -> Note:
        """Create a new note."""

        obj = await notes_repo.add(
            NoteModel(**data.model_dump(exclude_unset=True, exclude_none=True)),
        )
        await notes_repo.session.commit()
        return Note.model_validate(obj)

    @get(path="/notes/{note_id:uuid}", dependencies={"notes_repo": Provide(provide_note_details_repo)})
    async def get_note(
            self,
            notes_repo: NoteRepository,
            note_id: UUID = Parameter(
                title="Note ID",
                description="The note to retrieve.",
            ),
    ) -> Note:
        """Get an existing note."""
        obj = await notes_repo.get(note_id)
        return Note.model_validate(obj)

    @patch(
        path="/notes/{note_id:uuid}",
        dependencies={"notes_repo": Provide(provide_note_details_repo)},
    )
    async def update_note(
            self,
            notes_repo: NoteRepository,
            data: NoteUpdate,
            note_id: UUID = Parameter(
                title="Note ID",
                description="The note to update.",
            ),
    ) -> Note:
        """Update a note."""
        raw_obj = data.model_dump(exclude_unset=True, exclude_none=True)
        raw_obj.update({"id": note_id})
        obj = await notes_repo.update(NoteModel(**raw_obj))
        await notes_repo.session.commit()
        return Note.from_orm(obj)

    @delete(path="/notes/{note_id:uuid}")
    async def delete_note(
            self,
            notes_repo: NoteRepository,
            note_id: UUID = Parameter(
                title="Note ID",
                description="The note to delete.",
            ),
    ) -> None:
        """Delete a note from the system."""
        _ = await notes_repo.delete(note_id)
        await notes_repo.session.commit()