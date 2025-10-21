from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.dependencies import get_db
from app.dependencies.auth_dependencies import get_current_user
from app.controllers import AdminController
from app.models import User
from app.schemas import UserResponse, TicketResponse
from app.services.user_service import UserService
from pydantic import BaseModel

router = APIRouter(prefix="/admin", tags=["Admin"])

@router.get("/technicians/pending", response_model=List[UserResponse])
def get_pending_technicians(db: Session = Depends(get_db)):
    """Obter técnicos pendentes de aprovação"""
    return AdminController.get_pending_technicians(db)

@router.post("/technicians/{technician_id}/approve", response_model=UserResponse)
def approve_technician(
    technician_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Aprovar técnico (requer autenticação de admin)"""
    # Verificar se é admin
    role_str = str(current_user.role.value) if hasattr(current_user.role, 'value') else str(current_user.role)
    if role_str != "admin":
        raise HTTPException(status_code=403, detail="Acesso negado: apenas administradores")
    
    return AdminController.approve_technician(db, technician_id)

@router.get("/tickets", response_model=List[TicketResponse])
def get_all_tickets(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Obter todos os tickets (visão admin)"""
    return AdminController.get_all_tickets(db, skip, limit)

@router.post("/tickets/{ticket_id}/assign/{technician_id}", response_model=TicketResponse)
def assign_ticket(ticket_id: int, technician_id: int, db: Session = Depends(get_db)):
    """Atribuir ticket a um técnico"""
    return AdminController.assign_ticket(db, ticket_id, technician_id)

class ResetPasswordPayload(BaseModel):
    new_password: str

@router.get('/usuarios', response_model=List[UserResponse])
def list_users(db: Session = Depends(get_db)):
    """Lista todos os usuários (sem senhas)"""
    return AdminController.list_users(db)

@router.get('/servidores', response_model=List[UserResponse])
def list_servidores(db: Session = Depends(get_db)):
    """Lista apenas usuários com role=servidor"""
    users = UserService.get_users_by_role(db, "servidor")
    return [UserResponse.from_orm(u) for u in users]

@router.get('/tecnicos', response_model=List[UserResponse])
def list_technicians(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Lista apenas técnicos (requer autenticação de admin)"""
    # Verificar se é admin
    role_str = str(current_user.role.value) if hasattr(current_user.role, 'value') else str(current_user.role)
    if role_str != "admin":
        raise HTTPException(status_code=403, detail="Acesso negado: apenas administradores")
    
    users = UserService.get_users_by_role(db, "technician")
    return [UserResponse.from_orm(u) for u in users]

@router.get('/admins', response_model=List[UserResponse])
def list_admins(db: Session = Depends(get_db)):
    """Lista apenas admins"""
    users = UserService.get_users_by_role(db, "admin")
    return [UserResponse.from_orm(u) for u in users]

@router.post('/users/{user_id}/reset-password')
def reset_user_password(user_id: int, payload: ResetPasswordPayload, db: Session = Depends(get_db)):
    """Redefine a senha de um usuário (admin)"""
    return AdminController.reset_user_password(db, user_id, payload.new_password)

@router.get('/tickets', response_model=List[TicketResponse])
def get_tickets(status: str = None, db: Session = Depends(get_db)):
    """Obtém tickets com filtro opcional por status"""
    if status == "open":
        return AdminController.get_open_tickets(db)
    else:
        return AdminController.get_all_tickets(db)

@router.get('/tecnicos', response_model=List[UserResponse])
def get_technicians(db: Session = Depends(get_db)):
    """Obtém todos os técnicos para atribuição"""
    return AdminController.get_technicians(db)

@router.post('/tickets/{ticket_id}/assign', response_model=TicketResponse)
def assign_ticket(ticket_id: int, payload: dict, db: Session = Depends(get_db)):
    """Atribui um ticket a um técnico"""
    technician_id = payload.get('technician_id')
    if not technician_id:
        raise HTTPException(status_code=400, detail="technician_id é obrigatório")
    return AdminController.assign_ticket_to_technician(db, ticket_id, technician_id)

# === NOVOS ENDPOINTS PARA O SISTEMA DE ADMIN ===

@router.get('/tickets/open', response_model=List[TicketResponse])
def get_open_tickets_for_admin(db: Session = Depends(get_db)):
    """Obtém tickets abertos não atribuídos para o admin gerenciar"""
    from app.services.ticket_service import TicketService
    tickets = TicketService.get_open_tickets_for_admin(db)
    return [TicketResponse.from_orm(ticket) for ticket in tickets]

@router.get('/technicians', response_model=List[UserResponse])
def get_technicians_for_assignment(db: Session = Depends(get_db)):
    """Obtém técnicos disponíveis para atribuição"""
    return AdminController.get_technicians(db)

@router.get('/tickets/assigned', response_model=List[TicketResponse])
def get_assigned_tickets_for_admin(db: Session = Depends(get_db)):
    """Obtém tickets que já foram atribuídos a técnicos"""
    from app.services.ticket_service import TicketService
    tickets = TicketService.get_all_assigned_tickets(db)
    return [TicketResponse.from_orm(ticket) for ticket in tickets]