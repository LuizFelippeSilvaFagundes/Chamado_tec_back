from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.dependencies import get_db, require_technician_or_admin
from app.controllers import TechController
from app.models import User
from schemas import (
    TicketResponse, TicketWithHistory, TechDashboardStats,
    TicketHistoryCreate, TicketHistoryResponse
)

router = APIRouter(prefix="/tech", tags=["Technician"])

@router.get("/dashboard/stats", response_model=TechDashboardStats)
def get_dashboard_stats(current_user: User = Depends(require_technician_or_admin), db: Session = Depends(get_db)):
    """Obter estatísticas do dashboard do técnico"""
    return TechController.get_dashboard_stats(db, current_user)

@router.get("/tickets", response_model=List[TicketResponse])
def get_tech_tickets(skip: int = 0, limit: int = 100, current_user: User = Depends(require_technician_or_admin), db: Session = Depends(get_db)):
    """Obter tickets atribuídos ao técnico"""
    return TechController.get_assigned_tickets(db, current_user, skip, limit)

@router.get("/tickets/{ticket_id}", response_model=TicketWithHistory)
def get_tech_ticket_details(ticket_id: int, current_user: User = Depends(require_technician_or_admin), db: Session = Depends(get_db)):
    """Obter detalhes completos do ticket (com histórico)"""
    return TechController.get_ticket_details(db, ticket_id, current_user)

@router.put("/tickets/{ticket_id}/status", response_model=TicketResponse)
def update_ticket_status(ticket_id: int, status_update: dict, current_user: User = Depends(require_technician_or_admin), db: Session = Depends(get_db)):
    """Atualizar status do ticket"""
    return TechController.update_ticket_status(db, ticket_id, status_update, current_user)

@router.post("/tickets/{ticket_id}/history", response_model=TicketHistoryResponse)
def add_ticket_history(ticket_id: int, history: TicketHistoryCreate, current_user: User = Depends(require_technician_or_admin), db: Session = Depends(get_db)):
    """Adicionar entrada ao histórico do ticket"""
    return TechController.add_ticket_history(db, ticket_id, history, current_user)