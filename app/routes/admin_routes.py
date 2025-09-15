from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.dependencies import get_db, require_admin
from app.controllers import AdminController
from app.models import User
from schemas import UserResponse, TicketResponse

router = APIRouter(prefix="/admin", tags=["Admin"])

@router.get("/technicians/pending", response_model=List[UserResponse])
def get_pending_technicians(current_user: User = Depends(require_admin), db: Session = Depends(get_db)):
    """Obter técnicos pendentes de aprovação"""
    return AdminController.get_pending_technicians(db)

@router.post("/technicians/{technician_id}/approve", response_model=UserResponse)
def approve_technician(technician_id: int, current_user: User = Depends(require_admin), db: Session = Depends(get_db)):
    """Aprovar técnico"""
    return AdminController.approve_technician(db, technician_id)

@router.get("/tickets", response_model=List[TicketResponse])
def get_all_tickets(skip: int = 0, limit: int = 100, current_user: User = Depends(require_admin), db: Session = Depends(get_db)):
    """Obter todos os tickets (visão admin)"""
    return AdminController.get_all_tickets(db, skip, limit)

@router.post("/tickets/{ticket_id}/assign/{technician_id}", response_model=TicketResponse)
def assign_ticket(ticket_id: int, technician_id: int, current_user: User = Depends(require_admin), db: Session = Depends(get_db)):
    """Atribuir ticket a um técnico"""
    return AdminController.assign_ticket(db, ticket_id, technician_id)