from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from datetime import datetime
from app.models import User, Ticket, Comment, TicketHistory, StatusEnum
from app.schemas import (
    TicketCreate, TicketUpdate, CommentCreate, TicketHistoryCreate
)

class TicketService:
    @staticmethod
    def create_ticket(db: Session, ticket: TicketCreate, user_id: int) -> Ticket:
        """Cria um novo ticket"""
        # Remover campos que não existem no modelo Ticket
        ticket_data = ticket.dict()
        ticket_data.pop('username', None)  # Remove username se existir
        
        db_ticket = Ticket(
            **ticket_data,
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
    def get_unassigned_tickets(db: Session, skip: int = 0, limit: int = 100) -> List[Ticket]:
        """Busca tickets não atribuídos (disponíveis para técnicos)"""
        return db.query(Ticket).filter(Ticket.assigned_technician_id == None).offset(skip).limit(limit).all()

    @staticmethod
    def get_available_tickets_for_technician(db: Session, technician_id: int, skip: int = 0, limit: int = 100) -> List[Ticket]:
        """Busca tickets disponíveis para um técnico (atribuídos + não atribuídos)"""
        return db.query(Ticket).filter(
            or_(
                Ticket.assigned_technician_id == technician_id,
                Ticket.assigned_technician_id == None
            )
        ).offset(skip).limit(limit).all()

    @staticmethod
    def assign_ticket_to_self(db: Session, ticket_id: int, technician_id: int) -> Optional[Ticket]:
        """Permite que um técnico pegue um ticket não atribuído"""
        ticket = TicketService.get_ticket_by_id(db, ticket_id)
        if not ticket:
            return None
        
        # Verificar se ticket não está atribuído
        if ticket.assigned_technician_id is not None:
            return None  # Ticket já atribuído
        
        # Atribuir ao técnico
        ticket.assigned_technician_id = technician_id
        ticket.status = StatusEnum.in_progress
        ticket.assigned_by_admin = False  # Auto-atribuído pelo técnico
        db.commit()
        db.refresh(ticket)
        
        # Adicionar ao histórico
        TicketService.create_ticket_history(
            db, 
            TicketHistoryCreate(
                action="self_assigned",
                description=f"Técnico assumiu o ticket da fila"
            ), 
            ticket_id, 
            f"Técnico ID {technician_id}"
        )
        return ticket

    @staticmethod
    def get_all_tickets(db: Session, skip: int = 0, limit: int = 100) -> List[Ticket]:
        """Busca todos os tickets"""
        return db.query(Ticket).offset(skip).limit(limit).all()

    @staticmethod
    def get_tickets_by_status(db: Session, status, skip: int = 0, limit: int = 100) -> List[Ticket]:
        """Busca tickets por status"""
        # Converter string para Enum se necessário
        if isinstance(status, str):
            status = StatusEnum[status.replace("-", "_")]
        return db.query(Ticket).filter(Ticket.status == status).offset(skip).limit(limit).all()

    @staticmethod
    def update_ticket(db: Session, ticket_id: int, ticket_update: dict) -> Optional[Ticket]:
        """Atualiza um ticket"""
        db_ticket = TicketService.get_ticket_by_id(db, ticket_id)
        if db_ticket:
            for field, value in ticket_update.items():
                if value is not None:
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

    @staticmethod
    def assign_ticket_to_technician(db: Session, ticket_id: int, technician_id: int, assigned_by_admin: bool = False) -> Optional[Ticket]:
        """Atribui ticket a um técnico"""
        ticket = TicketService.get_ticket_by_id(db, ticket_id)
        if ticket:
            ticket.assigned_technician_id = technician_id
            ticket.status = StatusEnum.in_progress
            ticket.assigned_by_admin = assigned_by_admin
            db.commit()
            db.refresh(ticket)
            
            # Adicionar ao histórico
            action = "admin_assigned" if assigned_by_admin else "assigned"
            description = f"Ticket atribuído pelo admin ao técnico ID {technician_id}" if assigned_by_admin else f"Ticket atribuído ao técnico ID {technician_id}"
            
            TicketService.create_ticket_history(
                db, 
                TicketHistoryCreate(
                    action=action,
                    description=description
                ), 
                ticket_id, 
                "Sistema"
            )
        return ticket

    # Funções de Comentário
    @staticmethod
    def create_comment(db: Session, comment: CommentCreate, ticket_id: int, author: str) -> Comment:
        """Cria um comentário"""
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

    # Funções de Histórico de Ticket
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

    # Funções de Permissão
    @staticmethod
    def user_has_access_to_ticket(ticket: Ticket, user: User) -> bool:
        """Verifica se usuário tem acesso ao ticket"""
        # Usuário proprietário do ticket
        if ticket.user_id == user.id:
            return True
        
        # Técnico atribuído ao ticket
        if ticket.assigned_technician_id == user.id:
            return True
        
        # Admins têm acesso a todos
        role_str = str(user.role.value) if hasattr(user.role, 'value') else str(user.role)
        if role_str == "admin":
            return True
        
        return False

    @staticmethod
    def technician_has_access_to_ticket(ticket: Ticket, technician: User) -> bool:
        """Verifica se técnico tem acesso ao ticket"""
        # Técnico atribuído ao ticket
        if ticket.assigned_technician_id == technician.id:
            return True
        
        # Admins têm acesso a todos
        role_str = str(technician.role.value) if hasattr(technician.role, 'value') else str(technician.role)
        if role_str == "admin":
            return True
        
        return False

    # Funções de Estatísticas para Dashboard
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

    # === NOVOS MÉTODOS PARA O SISTEMA DE ADMIN ===
    
    @staticmethod
    def get_open_tickets_for_admin(db: Session, skip: int = 0, limit: int = 100) -> List[Ticket]:
        """Busca tickets abertos não atribuídos para o admin"""
        return db.query(Ticket).filter(
            and_(
                Ticket.status == StatusEnum.open,
                Ticket.assigned_technician_id == None
            )
        ).offset(skip).limit(limit).all()

    @staticmethod
    def get_tickets_assigned_by_admin(db: Session, technician_id: int, skip: int = 0, limit: int = 100) -> List[Ticket]:
        """Busca tickets atribuídos pelo admin para um técnico específico"""
        return db.query(Ticket).filter(
            and_(
                Ticket.assigned_technician_id == technician_id,
                Ticket.assigned_by_admin == True
            )
        ).offset(skip).limit(limit).all()

    @staticmethod
    def get_technician_assigned_tickets(db: Session, technician_id: int, skip: int = 0, limit: int = 100) -> List[Ticket]:
        """Busca todos os tickets atribuídos a um técnico (admin + auto-atribuídos)"""
        return db.query(Ticket).filter(Ticket.assigned_technician_id == technician_id).offset(skip).limit(limit).all()

    @staticmethod
    def get_available_tickets_for_tech_queue(db: Session, skip: int = 0, limit: int = 100) -> List[Ticket]:
        """Busca tickets disponíveis na fila para técnicos pegarem"""
        return db.query(Ticket).filter(
            and_(
                Ticket.status == StatusEnum.open,
                Ticket.assigned_technician_id == None
            )
        ).offset(skip).limit(limit).all()

    @staticmethod
    def get_all_assigned_tickets(db: Session, skip: int = 0, limit: int = 100) -> List[Ticket]:
        """Busca todos os tickets que foram atribuídos a técnicos"""
        return db.query(Ticket).filter(
            Ticket.assigned_technician_id != None
        ).offset(skip).limit(limit).all()
