from typing import List
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.services.user_service import UserService
from app.services.ticket_service import TicketService
from app.models import User
from schemas import UserResponse, TicketResponse

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
        if not technician or not UserService.is_technician_or_admin(technician):
            raise HTTPException(status_code=404, detail="Técnico não encontrado")
        
        # Atribuir ticket
        ticket = TicketService.assign_ticket_to_technician(db, ticket_id, technician_id)
        if not ticket:
            raise HTTPException(status_code=404, detail="Ticket não encontrado")
        
        return TicketResponse.from_orm(ticket)