from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.dependencies import get_db
from app.controllers import TechController
from app.models import User
from app.schemas import (
    TicketResponse, TicketWithHistory, TechDashboardStats,
    TicketHistoryCreate, TicketHistoryResponse
)
from app.schemas import UserResponse
from app.services.user_service import UserService

router = APIRouter(prefix="/tecnico", tags=["Técnico"])

@router.get("/dashboard/stats")
def get_dashboard_stats(db: Session = Depends(get_db)):
    """Obter estatísticas do dashboard do técnico"""
    return {"message": "Endpoint desabilitado - autenticação removida"}

@router.get("/tickets", response_model=List[TicketResponse])
def get_tech_tickets(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Obter tickets disponíveis (atribuídos + não atribuídos)"""
    return []

@router.get("/tickets/assigned", response_model=List[TicketResponse])
def get_assigned_tickets(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Obter apenas tickets já atribuídos ao técnico"""
    return []

@router.get("/tickets/available", response_model=List[TicketResponse])
def get_available_tickets(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Obter tickets não atribuídos (disponíveis para pegar)"""
    return []

@router.get("/usuarios", response_model=List[UserResponse])
def list_users_by_role(db: Session = Depends(get_db)):
    """Lista usuários por áreas, visível a técnicos e admins: servidores, técnicos e admins"""
    users = UserService.get_users_by_role(db, "servidor") + UserService.get_users_by_role(db, "technician") + UserService.get_users_by_role(db, "admin")
    return [UserResponse.from_orm(u) for u in users]

@router.get("/tickets/{ticket_id}")
def get_tech_ticket_details(ticket_id: int, db: Session = Depends(get_db)):
    """Obter detalhes completos do ticket (com histórico)"""
    return {"message": "Endpoint desabilitado - autenticação removida"}

@router.put("/tickets/{ticket_id}/status")
def update_ticket_status(ticket_id: int, status_update: dict, db: Session = Depends(get_db)):
    """Atualizar status do ticket"""
    return {"message": "Endpoint desabilitado - autenticação removida"}

@router.post("/tickets/{ticket_id}/history")
def add_ticket_history(ticket_id: int, history: TicketHistoryCreate, db: Session = Depends(get_db)):
    """Adicionar entrada ao histórico do ticket"""
    return {"message": "Endpoint desabilitado - autenticação removida"}

@router.post("/tickets/{ticket_id}/take")
def take_ticket(ticket_id: int, db: Session = Depends(get_db)):
    """Pegar um ticket não atribuído"""
    return {"message": "Endpoint desabilitado - autenticação removida"}
