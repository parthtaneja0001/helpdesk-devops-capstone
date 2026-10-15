from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from .models import Priority, Status


class TicketCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str = ""
    requester: str = Field(min_length=1, max_length=120)
    assignee: str | None = None
    priority: Priority = Priority.medium


class TicketUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = None
    requester: str | None = Field(default=None, min_length=1, max_length=120)
    assignee: str | None = None
    status: Status | None = None
    priority: Priority | None = None


class TicketOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str
    requester: str
    assignee: str | None
    status: Status
    priority: Priority
    created_at: datetime
    updated_at: datetime


class TicketStats(BaseModel):
    total: int
    open: int
    in_progress: int
    resolved: int
    closed: int
    urgent: int
