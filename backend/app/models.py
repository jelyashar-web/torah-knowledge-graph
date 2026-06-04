"""SQLAlchemy models for operational data in PostgreSQL."""

import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class JobStatus(str, enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class IngestionJob(Base):
    __tablename__ = "ingestion_jobs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    book_title: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    source_type: Mapped[str] = mapped_column(
        String(50), nullable=False, default="sefaria"
    )
    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default=JobStatus.PENDING.value,
        index=True,
    )
    total_refs: Mapped[int | None] = mapped_column(Integer, nullable=True)
    fetched_refs: Mapped[int | None] = mapped_column(Integer, nullable=True, default=0)
    failed_refs: Mapped[int | None] = mapped_column(Integer, nullable=True, default=0)
    errors: Mapped[list[dict] | None] = mapped_column(JSONB, nullable=True, default=list)
    meta: Mapped[dict | None] = mapped_column(JSONB, nullable=True, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    def __repr__(self) -> str:
        return (
            f"<IngestionJob id={self.id} book={self.book_title} "
            f"status={self.status.value} progress={self.fetched_refs}/{self.total_refs}>"
        )
