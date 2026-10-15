import enum
from datetime import datetime, timezone

from sqlalchemy import DateTime, Enum, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from .database import Base


class Status(str, enum.Enum):
    open = "open"
    in_progress = "in_progress"
    resolved = "resolved"
    closed = "closed"


class Priority(str, enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"
    urgent = "urgent"


def _now():
    return datetime.now(timezone.utc)


class Ticket(Base):
    __tablename__ = "tickets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, default="", nullable=False)
    requester: Mapped[str] = mapped_column(String(120), nullable=False)
    assignee: Mapped[str | None] = mapped_column(String(120), nullable=True)
    status: Mapped[Status] = mapped_column(
        Enum(Status, name="ticket_status"), default=Status.open, nullable=False
    )
    priority: Mapped[Priority] = mapped_column(
        Enum(Priority, name="ticket_priority"), default=Priority.medium, nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_now, onupdate=_now
    )
