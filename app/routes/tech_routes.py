from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.dependencies import get_db
from app.dependencies.auth_dependencies import get_current_user
from app.controllers import TechController
from app.models import User
from app.schemas import (
    TicketResponse, TicketWithHistory, TechDashboardStats,
    TicketHistoryCreate, TicketHistoryResponse
)
from app.schemas import UserResponse
from app.services.user_service import UserService

router = APIRouter(prefix="/tech", tags=["Técnico"])

@router.get("/dashboard/stats", response_model=TechDashboardStats)
def get_dashboard_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obter estatísticas do dashboard do técnico"""
    from app.services.ticket_service import TicketService
    
    # Verificar se é técnico ou admin
    role_str = str(current_user.role.value) if hasattr(current_user.role, 'value') else str(current_user.role)
    if role_str not in ["technician", "admin"]:
        raise HTTPException(status_code=403, detail="Acesso negado: apenas técnicos e admins")
    
    stats = TicketService.get_tech_dashboard_stats(db, current_user.id)
    return stats

@router.get("/tickets", response_model=List[TicketResponse])
def get_tech_tickets(
    current_user: User = Depends(get_current_user),
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db)
):
    """Obter tickets disponíveis (atribuídos ao técnico + não atribuídos)"""
    from app.services.ticket_service import TicketService
    
    # Verificar se é técnico ou admin
    role_str = str(current_user.role.value) if hasattr(current_user.role, 'value') else str(current_user.role)
    if role_str not in ["technician", "admin"]:
        raise HTTPException(status_code=403, detail="Acesso negado: apenas técnicos e admins")
    
    tickets = TicketService.get_available_tickets_for_technician(db, current_user.id, skip, limit)
    return [TicketResponse.from_orm(ticket) for ticket in tickets]

@router.get("/tickets/assigned", response_model=List[TicketResponse])
def get_assigned_tickets(
    current_user: User = Depends(get_current_user),
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db)
):
    """Obter apenas tickets já atribuídos ao técnico logado"""
    from app.services.ticket_service import TicketService
    
    # Verificar se é técnico ou admin
    role_str = str(current_user.role.value) if hasattr(current_user.role, 'value') else str(current_user.role)
    if role_str not in ["technician", "admin"]:
        raise HTTPException(status_code=403, detail="Acesso negado: apenas técnicos e admins")
    
    tickets = TicketService.get_technician_assigned_tickets(db, current_user.id, skip, limit)
    return [TicketResponse.from_orm(ticket) for ticket in tickets]

@router.get("/tickets/available", response_model=List[TicketResponse])
def get_available_tickets(
    current_user: User = Depends(get_current_user),
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db)
):
    """Obter tickets não atribuídos (disponíveis para pegar)"""
    from app.services.ticket_service import TicketService
    
    # Verificar se é técnico ou admin
    role_str = str(current_user.role.value) if hasattr(current_user.role, 'value') else str(current_user.role)
    if role_str not in ["technician", "admin"]:
        raise HTTPException(status_code=403, detail="Acesso negado: apenas técnicos e admins")
    
    tickets = TicketService.get_available_tickets_for_tech_queue(db, skip, limit)
    return [TicketResponse.from_orm(ticket) for ticket in tickets]

# === NOVOS ENDPOINTS PARA TÉCNICOS ===

@router.get("/tickets/admin-assigned", response_model=List[TicketResponse])
def get_admin_assigned_tickets(
    current_user: User = Depends(get_current_user),
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db)
):
    """Obtém tickets atribuídos pelo admin ao técnico logado"""
    from app.services.ticket_service import TicketService
    
    # Verificar se é técnico ou admin
    role_str = str(current_user.role.value) if hasattr(current_user.role, 'value') else str(current_user.role)
    if role_str not in ["technician", "admin"]:
        raise HTTPException(status_code=403, detail="Acesso negado: apenas técnicos e admins")
    
    tickets = TicketService.get_tickets_assigned_by_admin(db, current_user.id, skip, limit)
    return [TicketResponse.from_orm(ticket) for ticket in tickets]

@router.post("/tickets/{ticket_id}/take", response_model=TicketResponse)
def take_ticket(
    ticket_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Pegar um ticket não atribuído da fila"""
    from app.services.ticket_service import TicketService
    
    # Verificar se é técnico ou admin
    role_str = str(current_user.role.value) if hasattr(current_user.role, 'value') else str(current_user.role)
    if role_str not in ["technician", "admin"]:
        raise HTTPException(status_code=403, detail="Acesso negado: apenas técnicos e admins")
    
    ticket = TicketService.assign_ticket_to_self(db, ticket_id, current_user.id)
    if not ticket:
        raise HTTPException(status_code=400, detail="Ticket não encontrado ou já atribuído")
    return TicketResponse.from_orm(ticket)

@router.get("/usuarios", response_model=List[UserResponse])
def list_users_by_role(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Lista usuários por áreas, visível a técnicos e admins: servidores, técnicos e admins"""
    # Verificar se é técnico ou admin
    role_str = str(current_user.role.value) if hasattr(current_user.role, 'value') else str(current_user.role)
    if role_str not in ["technician", "admin"]:
        raise HTTPException(status_code=403, detail="Acesso negado: apenas técnicos e admins")
    
    users = UserService.get_users_by_role(db, "servidor") + UserService.get_users_by_role(db, "technician") + UserService.get_users_by_role(db, "admin")
    return [UserResponse.from_orm(u) for u in users]

@router.get("/todos", response_model=List[UserResponse])
def list_all_tecnicos(db: Session = Depends(get_db)):
    """Lista apenas técnicos (role=technician)"""
    users = UserService.get_users_by_role(db, "technician")
    return [UserResponse.from_orm(u) for u in users]

@router.get("/tickets/{ticket_id}", response_model=TicketWithHistory)
def get_tech_ticket_details(
    ticket_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obter detalhes completos do ticket (com histórico)"""
    from app.services.ticket_service import TicketService
    
    # Verificar se é técnico ou admin
    role_str = str(current_user.role.value) if hasattr(current_user.role, 'value') else str(current_user.role)
    if role_str not in ["technician", "admin"]:
        raise HTTPException(status_code=403, detail="Acesso negado: apenas técnicos e admins")
    
    ticket = TicketService.get_ticket_by_id(db, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket não encontrado")
    
    # Verificar se técnico tem acesso ao ticket
    if not TicketService.technician_has_access_to_ticket(ticket, current_user):
        raise HTTPException(status_code=403, detail="Acesso negado a este ticket")
    
    return TicketWithHistory.from_orm(ticket)

@router.put("/tickets/{ticket_id}/status")
def update_ticket_status(
    ticket_id: int, 
    status_update: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Atualizar status do ticket"""
    from app.services.ticket_service import TicketService
    from app.schemas import TicketUpdate
    
    # Verificar se é técnico ou admin
    role_str = str(current_user.role.value) if hasattr(current_user.role, 'value') else str(current_user.role)
    if role_str not in ["technician", "admin"]:
        raise HTTPException(status_code=403, detail="Acesso negado: apenas técnicos e admins")
    
    ticket = TicketService.get_ticket_by_id(db, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket não encontrado")
    
    # Verificar se técnico tem acesso ao ticket
    if not TicketService.technician_has_access_to_ticket(ticket, current_user):
        raise HTTPException(status_code=403, detail="Acesso negado a este ticket")
    
    updated_ticket = TicketService.update_ticket(db, ticket_id, status_update)
    return TicketResponse.from_orm(updated_ticket)

@router.post("/tickets/{ticket_id}/history", response_model=TicketHistoryResponse)
def add_ticket_history(
    ticket_id: int, 
    history: TicketHistoryCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Adicionar entrada ao histórico do ticket"""
    from app.services.ticket_service import TicketService
    
    # Verificar se é técnico ou admin
    role_str = str(current_user.role.value) if hasattr(current_user.role, 'value') else str(current_user.role)
    if role_str not in ["technician", "admin"]:
        raise HTTPException(status_code=403, detail="Acesso negado: apenas técnicos e admins")
    
    ticket = TicketService.get_ticket_by_id(db, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket não encontrado")
    
    # Verificar se técnico tem acesso ao ticket
    if not TicketService.technician_has_access_to_ticket(ticket, current_user):
        raise HTTPException(status_code=403, detail="Acesso negado a este ticket")
    
    history_entry = TicketService.create_ticket_history(
        db, history, ticket_id, current_user.full_name
    )
    return TicketHistoryResponse.from_orm(history_entry)
