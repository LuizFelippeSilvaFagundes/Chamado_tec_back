from typing import List
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.services.ticket_service import TicketService
from app.models import User
from schemas import (
    TicketResponse, TicketWithHistory, TechDashboardStats,
    TicketHistoryCreate, TicketHistoryResponse
)

class TechController:
    @staticmethod
    def get_dashboard_stats(db: Session, technician: User) -> TechDashboardStats:
        """Obtém estatísticas do dashboard do técnico"""
        stats = TicketService.get_tech_dashboard_stats(db, technician.id)
        return TechDashboardStats(**stats)

    @staticmethod
    def get_assigned_tickets(db: Session, technician: User, skip: int = 0, limit: int = 100) -> List[TicketResponse]:
        """Obtém tickets atribuídos ao técnico"""
        tickets = TicketService.get_tickets_by_technician(db, technician.id, skip, limit)
        return [TicketResponse.from_orm(ticket) for ticket in tickets]

    @staticmethod
    def get_ticket_details(db: Session, ticket_id: int, technician: User) -> TicketWithHistory:
        """Obtém detalhes completos do ticket"""
        ticket = TicketService.get_ticket_by_id(db, ticket_id)
        if not ticket:
            raise HTTPException(status_code=404, detail="Ticket não encontrado")
        
        # Verificar se o técnico tem acesso ao ticket
        if not TicketService.technician_has_access_to_ticket(ticket, technician):
            raise HTTPException(status_code=403, detail="Acesso negado")
        
        return TicketWithHistory.from_orm(ticket)

    @staticmethod
    def update_ticket_status(db: Session, ticket_id: int, status_update: dict, technician: User) -> TicketResponse:
        """Atualiza status do ticket"""
        ticket = TicketService.get_ticket_by_id(db, ticket_id)
        if not ticket:
            raise HTTPException(status_code=404, detail="Ticket não encontrado")
        
        # Verificar se o técnico tem acesso ao ticket
        if not TicketService.technician_has_access_to_ticket(ticket, technician):
            raise HTTPException(status_code=403, detail="Acesso negado")
        
        # Atualizar status
        updated_ticket = TicketService.update_ticket(db, ticket_id, status_update)
        
        # Adicionar ao histórico
        TicketService.create_ticket_history(db, TicketHistoryCreate(
            action="status_change",
            description=f"Status alterado para {status_update.get('status', 'N/A')}"
        ), ticket_id, technician.full_name)
        
        return TicketResponse.from_orm(updated_ticket)

    @staticmethod
    def add_ticket_history(db: Session, ticket_id: int, history: TicketHistoryCreate, technician: User) -> TicketHistoryResponse:
        """Adiciona entrada ao histórico do ticket"""
        ticket = TicketService.get_ticket_by_id(db, ticket_id)
        if not ticket:
            raise HTTPException(status_code=404, detail="Ticket não encontrado")
        
        # Verificar se o técnico tem acesso ao ticket
        if not TicketService.technician_has_access_to_ticket(ticket, technician):
            raise HTTPException(status_code=403, detail="Acesso negado")
        
        # Criar entrada no histórico
        db_history = TicketService.create_ticket_history(db, history, ticket_id, technician.full_name)
        return TicketHistoryResponse.from_orm(db_history)