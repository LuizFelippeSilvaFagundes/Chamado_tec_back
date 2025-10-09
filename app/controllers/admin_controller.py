from typing import List
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.services.user_service import UserService
from app.services.ticket_service import TicketService
from app.models import User
from app.schemas import UserResponse, TicketResponse
from app.services.auth_service import AuthService

class AdminController:
    @staticmethod
    def get_pending_technicians(db: Session) -> List[UserResponse]:
        """Obtém técnicos pendentes de aprovação"""
        technicians = UserService.get_pending_technicians(db)
        return [UserResponse.from_orm(tech) for tech in technicians]

    @staticmethod
    def approve_technician(db: Session, technician_id: int) -> UserResponse:
        """Aprova um técnico"""
        technician = UserService.approve_technician(db, technician_id)
        if not technician:
            raise HTTPException(status_code=404, detail="Técnico não encontrado")
        return UserResponse.from_orm(technician)

    @staticmethod
    def get_all_tickets(db: Session, skip: int = 0, limit: int = 100) -> List[TicketResponse]:
        """Obtém todos os tickets (visão admin)"""
        tickets = TicketService.get_all_tickets(db, skip, limit)
        return [TicketResponse.from_orm(ticket) for ticket in tickets]

    @staticmethod
    def assign_ticket(db: Session, ticket_id: int, technician_id: int) -> TicketResponse:
        """Atribui ticket a um técnico"""
        # Verificar se o técnico existe
        technician = UserService.get_user_by_id(db, technician_id)
        if not technician or technician.role not in ["technician", "admin"]:
            raise HTTPException(status_code=404, detail="Técnico não encontrado")
        
        # Atribuir ticket
        ticket = TicketService.assign_ticket_to_technician(db, ticket_id, technician_id)
        if not ticket:
            raise HTTPException(status_code=404, detail="Ticket não encontrado")
        
        return TicketResponse.from_orm(ticket)

    @staticmethod
    def list_users(db: Session) -> List[UserResponse]:
        """Lista todos os usuários (sem senha)"""
        users = db.query(User).all()
        return [UserResponse.from_orm(u) for u in users]

    @staticmethod
    def reset_user_password(db: Session, user_id: int, new_password: str):
        """Admin define nova senha para um usuário"""
        user = UserService.get_user_by_id(db, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="Usuário não encontrado")
        hashed = AuthService.get_password_hash(new_password)
        UserService.update_user_password(db, user_id, hashed)
        return {"detail": "Senha redefinida"}

    @staticmethod
    def get_open_tickets(db: Session) -> List[TicketResponse]:
        """Obtém todos os tickets abertos para atribuição"""
        tickets = TicketService.get_tickets_by_status(db, "open")
        return [TicketResponse.from_orm(ticket) for ticket in tickets]

    @staticmethod
    def get_technicians(db: Session) -> List[UserResponse]:
        """Obtém todos os técnicos para atribuição"""
        technicians = UserService.get_users_by_role(db, "technician")
        return [UserResponse.from_orm(tech) for tech in technicians]

    @staticmethod
    def assign_ticket_to_technician(db: Session, ticket_id: int, technician_id: int) -> TicketResponse:
        """Atribui um ticket a um técnico"""
        # Verificar se o técnico existe
        technician = UserService.get_user_by_id(db, technician_id)
        if not technician or technician.role != "technician":
            raise HTTPException(status_code=404, detail="Técnico não encontrado")
        
        # Atribuir ticket
        ticket = TicketService.assign_ticket_to_technician(db, ticket_id, technician_id)
        if not ticket:
            raise HTTPException(status_code=404, detail="Ticket não encontrado")
        
        return TicketResponse.from_orm(ticket)