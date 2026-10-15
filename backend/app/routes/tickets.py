from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Priority, Status, Ticket
from ..schemas import TicketCreate, TicketOut, TicketStats, TicketUpdate

router = APIRouter(prefix="/api/tickets", tags=["tickets"])


@router.get("", response_model=list[TicketOut])
def list_tickets(
    status: Status | None = None,
    priority: Priority | None = None,
    db: Session = Depends(get_db),
):
    query = select(Ticket).order_by(Ticket.created_at.desc(), Ticket.id.desc())
    if status:
        query = query.where(Ticket.status == status)
    if priority:
        query = query.where(Ticket.priority == priority)
    return db.scalars(query).all()


# Declared before "/{ticket_id}" so "stats" is not parsed as an id.
@router.get("/stats", response_model=TicketStats)
def ticket_stats(db: Session = Depends(get_db)):
    counts = dict(db.execute(select(Ticket.status, func.count()).group_by(Ticket.status)).all())
    urgent = db.scalar(
        select(func.count()).select_from(Ticket).where(
            Ticket.priority == Priority.urgent, Ticket.status.in_([Status.open, Status.in_progress])
        )
    )
    return TicketStats(
        total=sum(counts.values()),
        open=counts.get(Status.open, 0),
        in_progress=counts.get(Status.in_progress, 0),
        resolved=counts.get(Status.resolved, 0),
        closed=counts.get(Status.closed, 0),
        urgent=urgent or 0,
    )


@router.get("/{ticket_id}", response_model=TicketOut)
def get_ticket(ticket_id: int, db: Session = Depends(get_db)):
    ticket = db.get(Ticket, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return ticket


@router.post("", response_model=TicketOut, status_code=201)
def create_ticket(payload: TicketCreate, db: Session = Depends(get_db)):
    ticket = Ticket(**payload.model_dump())
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    return ticket


@router.put("/{ticket_id}", response_model=TicketOut)
def update_ticket(ticket_id: int, payload: TicketUpdate, db: Session = Depends(get_db)):
    ticket = db.get(Ticket, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(ticket, field, value)
    db.commit()
    db.refresh(ticket)
    return ticket


@router.delete("/{ticket_id}", status_code=204)
def delete_ticket(ticket_id: int, db: Session = Depends(get_db)):
    ticket = db.get(Ticket, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    db.delete(ticket)
    db.commit()
    return Response(status_code=204)
