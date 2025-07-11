from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional
import datetime
from enum import Enum

app = FastAPI(title="Ticket API", version="1.0.0")

# Simple enums for validation
class TicketStatus(str, Enum):
    open = "open"
    in_progress = "in_progress"
    closed = "closed"


class TicketPriority(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


# Main ticket model
class Ticket(BaseModel):
    id: Optional[int] = None
    title: str = Field(..., min_length=1, max_length=100)
    description: str = Field(..., min_length=5, max_length=500)
    status: TicketStatus = TicketStatus.open
    priority: TicketPriority = TicketPriority.medium
    assignee: Optional[str] = None
    created_at: Optional[datetime.datetime] = None


# Simple create model
class TicketCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    description: str = Field(..., min_length=5, max_length=500)
    priority: TicketPriority = TicketPriority.medium
    assignee: Optional[str] = None


# In-memory storage
tickets_db = []
next_id = 1


@app.get("/")
async def root():
    return {"message": "Welcome to the Ticket API"}


@app.post("/tickets/", response_model=Ticket)
async def create_ticket(ticket: TicketCreate):
    global next_id
    
    new_ticket = Ticket(
        id=next_id,
        title=ticket.title,
        description=ticket.description,
        priority=ticket.priority,
        assignee=ticket.assignee,
        created_at=datetime.datetime.now()
    )
    tickets_db.append(new_ticket)
    next_id += 1
    return new_ticket


@app.get("/tickets/", response_model=List[Ticket])
async def get_tickets():
    return tickets_db


@app.get("/tickets/{ticket_id}", response_model=Ticket)
async def get_ticket(ticket_id: int):
    # Find ticket by ID
    ticket = next((t for t in tickets_db if t.id == ticket_id), None)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return ticket


@app.put("/tickets/{ticket_id}", response_model=Ticket)
async def update_ticket(ticket_id: int, title: Optional[str] = None, 
                       status: Optional[TicketStatus] = None,
                       assignee: Optional[str] = None):
    # Find ticket
    ticket = next((t for t in tickets_db if t.id == ticket_id), None)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    # Update fields if provided
    if title:
        ticket.title = title
    if status:
        ticket.status = status
    if assignee is not None:  # Allow empty string to clear assignee
        ticket.assignee = assignee
    
    return ticket


@app.delete("/tickets/{ticket_id}")
async def delete_ticket(ticket_id: int):
    global tickets_db
    # Find and remove ticket
    ticket = next((t for t in tickets_db if t.id == ticket_id), None)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    tickets_db = [t for t in tickets_db if t.id != ticket_id]
    return {"message": "Ticket deleted"}


def main():
    print("Hello from the ticket-api!")

if __name__ == "__main__":
    main()
