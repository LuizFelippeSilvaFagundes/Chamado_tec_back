from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List, Optional
from datetime import datetime
from app.models import Ticket, TicketHistory, Comment, User, StatusEnum
from schemas import TicketCreate, TicketUpdate, CommentCreate, TicketHistoryCreate

class TicketService:
    @staticmethod
    def create_ticket(db: Session, ticket: TicketCreate, user_id: int) -> Ticket:
        """Cria um novo ticket"""
        db_ticket = Ticket(
            **ticket.dict(),
            user_id=user_id
        )
        db.add(db_ticket)
        db.commit()
        db.refresh(db_ticket)
        return db_ticket

    @staticmethod
    def get_ticket_by_id(db: Session, ticket_id: int) -> Optional[Ticket]:
        """Busca ticket por ID"""
        return db.query(Ticket).filter(Ticket.id == ticket_id).first()

    @staticmethod
    def get_tickets_by_user(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[Ticket]:
        """Busca tickets de um usuário"""
        return db.query(Ticket).filter(Ticket.user_id == user_id).offset(skip).limit(limit).all()

    @staticmethod
    def get_tickets_by_technician(db: Session, technician_id: int, skip: int = 0, limit: int = 100) -> List[Ticket]:
        """Busca tickets atribuídos a um técnico"""
        return db.query(Ticket).filter(Ticket.assigned_technician_id == technician_id).offset(skip).limit(limit).all()

    @staticmethod
    def get_all_tickets(db: Session, skip: int = 0, limit: int = 100) -> List[Ticket]:
        """Busca todos os tickets (admin)"""
        return db.query(Ticket).offset(skip).limit(limit).all()

    @staticmethod
    def get_tickets_by_status(db: Session, status: StatusEnum, skip: int = 0, limit: int = 100) -> List[Ticket]:
        """Busca tickets por status"""
        return db.query(Ticket).filter(Ticket.status == status).offset(skip).limit(limit).all()

    @staticmethod
    def assign_ticket_to_technician(db: Session, ticket_id: int, technician_id: int) -> Optional[Ticket]:
        """Atribui ticket a um técnico"""
        ticket = TicketService.get_ticket_by_id(db, ticket_id)
        if ticket:
            ticket.assigned_technician_id = technician_id
            ticket.status = StatusEnum.in_progress
            db.commit()
            db.refresh(ticket)
            
            # Adicionar ao histórico
            TicketService.create_ticket_history(db, TicketHistoryCreate(
                action="assigned",
                description=f"Ticket atribuído ao técnico ID {technician_id}"
            ), ticket_id, "Sistema")
        return ticket

    @staticmethod
    def update_ticket(db: Session, ticket_id: int, ticket_update: dict) -> Optional[Ticket]:
        """Atualiza um ticket"""
        db_ticket = TicketService.get_ticket_by_id(db, ticket_id)
        if db_ticket:
            for field, value in ticket_update.items():
                if hasattr(db_ticket, field) and value is not None:
                    setattr(db_ticket, field, value)
            db_ticket.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(db_ticket)
        return db_ticket

    @staticmethod
    def delete_ticket(db: Session, ticket_id: int) -> bool:
        """Deleta um ticket"""
        db_ticket = TicketService.get_ticket_by_id(db, ticket_id)
        if db_ticket:
            db.delete(db_ticket)
            db.commit()
            return True
        return False

    # Métodos para Comentários
    @staticmethod
    def create_comment(db: Session, comment: CommentCreate, ticket_id: int, author: str) -> Comment:
        """Cria um comentário no ticket"""
        db_comment = Comment(
            **comment.dict(),
            ticket_id=ticket_id,
            author=author
        )
        db.add(db_comment)
        db.commit()
        db.refresh(db_comment)
        return db_comment

    @staticmethod
    def get_comments_by_ticket(db: Session, ticket_id: int) -> List[Comment]:
        """Busca comentários de um ticket"""
        return db.query(Comment).filter(Comment.ticket_id == ticket_id).order_by(Comment.created_at).all()

    @staticmethod
    def delete_comment(db: Session, comment_id: int) -> bool:
        """Deleta um comentário"""
        db_comment = db.query(Comment).filter(Comment.id == comment_id).first()
        if db_comment:
            db.delete(db_comment)
            db.commit()
            return True
        return False

    # Métodos para Histórico
    @staticmethod
    def create_ticket_history(db: Session, history: TicketHistoryCreate, ticket_id: int, technician_name: str) -> TicketHistory:
        """Cria entrada no histórico do ticket"""
        db_history = TicketHistory(
            **history.dict(),
            ticket_id=ticket_id,
            technician_name=technician_name
        )
        db.add(db_history)
        db.commit()
        db.refresh(db_history)
        return db_history

    @staticmethod
    def get_ticket_history(db: Session, ticket_id: int) -> List[TicketHistory]:
        """Busca histórico de um ticket"""
        return db.query(TicketHistory).filter(TicketHistory.ticket_id == ticket_id).order_by(TicketHistory.timestamp).all()

    # Métodos para Dashboard/Estatísticas
    @staticmethod
    def get_tech_dashboard_stats(db: Session, technician_id: int) -> dict:
        """Obtém estatísticas do dashboard do técnico"""
        total_tickets = db.query(Ticket).filter(Ticket.assigned_technician_id == technician_id).count()
        pending_tickets = db.query(Ticket).filter(
            and_(Ticket.assigned_technician_id == technician_id, Ticket.status == StatusEnum.pending)
        ).count()
        in_progress_tickets = db.query(Ticket).filter(
            and_(Ticket.assigned_technician_id == technician_id, Ticket.status == StatusEnum.in_progress)
        ).count()
        resolved_tickets = db.query(Ticket).filter(
            and_(Ticket.assigned_technician_id == technician_id, Ticket.status == StatusEnum.resolved)
        ).count()
        
        # Tickets em atraso (SLA vencido)
        overdue_tickets = db.query(Ticket).filter(
            and_(
                Ticket.assigned_technician_id == technician_id,
                Ticket.sla_deadline < datetime.utcnow(),
                Ticket.status.in_([StatusEnum.pending, StatusEnum.in_progress])
            )
        ).count()
        
        # Tempo médio de resolução (simplificado)
        avg_resolution_time = 0.0  # Implementar cálculo real baseado no histórico
        
        return {
            "total_tickets": total_tickets,
            "pending_tickets": pending_tickets,
            "in_progress_tickets": in_progress_tickets,
            "resolved_tickets": resolved_tickets,
            "overdue_tickets": overdue_tickets,
            "avg_resolution_time": avg_resolution_time
        }

    @staticmethod
    def user_has_access_to_ticket(ticket: Ticket, user: User) -> bool:
        """Verifica se usuário tem acesso ao ticket"""
        if user.role == "admin":
            return True
        if user.role == "technician" and ticket.assigned_technician_id == user.id:
            return True
        if ticket.user_id == user.id:
            return True
        return False

    @staticmethod
    def technician_has_access_to_ticket(ticket: Ticket, technician: User) -> bool:
        """Verifica se técnico tem acesso ao ticket"""
        return (ticket.assigned_technician_id == technician.id or 
                technician.role == "admin")