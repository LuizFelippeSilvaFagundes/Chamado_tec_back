from typing import List
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.services.ticket_service import TicketService
from app.models import User, Comment
from app.schemas import (
    TicketCreate, TicketUpdate, TicketResponse, TicketWithComments, 
    CommentCreate, CommentResponse
)

class TicketController:
    @staticmethod
    def create_ticket(db: Session, ticket: TicketCreate, user: User) -> TicketResponse:
        """Cria um novo ticket"""
        # Se não há usuário autenticado, usar usuário padrão (ID 1) ou criar um
        if user is None:
            default_user = db.query(User).filter(User.id == 1).first()
            if not default_user:
                # Criar usuário padrão se não existir
                default_user = User(
                    username="sistema",
                    full_name="Sistema",
                    role="servidor",
                    is_active=True,
                    is_approved=True
                )
                db.add(default_user)
                db.commit()
                db.refresh(default_user)
            user_id = default_user.id
        else:
            user_id = user.id
            
        db_ticket = TicketService.create_ticket(db, ticket, user_id)
        return TicketResponse.from_orm(db_ticket)

    @staticmethod
    def get_user_tickets(db: Session, user: User, skip: int = 0, limit: int = 100) -> List[TicketWithComments]:
        """Obtém tickets do usuário"""
        if user is None:
            return []
        tickets = TicketService.get_tickets_by_user(db, user.id, skip, limit)
        return [TicketWithComments.from_orm(ticket) for ticket in tickets]

    @staticmethod
    def get_ticket_details(db: Session, ticket_id: int, user: User) -> TicketWithComments:
        """Obtém detalhes de um ticket específico"""
        ticket = TicketService.get_ticket_by_id(db, ticket_id)
        if not ticket:
            raise HTTPException(status_code=404, detail="Ticket não encontrado")
        
        # Sem autenticação, permitir acesso a todos os tickets
        return TicketWithComments.from_orm(ticket)

    @staticmethod
    def update_ticket(db: Session, ticket_id: int, ticket_update: TicketUpdate, user: User) -> TicketResponse:
        """Atualiza um ticket"""
        ticket = TicketService.get_ticket_by_id(db, ticket_id)
        if not ticket:
            raise HTTPException(status_code=404, detail="Ticket não encontrado")
        
        # Sem autenticação, permitir atualização
        updated_ticket = TicketService.update_ticket(db, ticket_id, ticket_update.dict(exclude_unset=True))
        return TicketResponse.from_orm(updated_ticket)

    @staticmethod
    def delete_ticket(db: Session, ticket_id: int, user: User) -> dict:
        """Deleta um ticket"""
        ticket = TicketService.get_ticket_by_id(db, ticket_id)
        if not ticket:
            raise HTTPException(status_code=404, detail="Ticket não encontrado")
        
        # Sem autenticação, permitir deleção
        success = TicketService.delete_ticket(db, ticket_id)
        if not success:
            raise HTTPException(status_code=500, detail="Erro ao deletar ticket")
        
        return {"message": "Ticket deletado com sucesso"}

    @staticmethod
    def add_comment(db: Session, ticket_id: int, comment: CommentCreate, user: User) -> CommentResponse:
        """Adiciona comentário ao ticket"""
        ticket = TicketService.get_ticket_by_id(db, ticket_id)
        if not ticket:
            raise HTTPException(status_code=404, detail="Ticket não encontrado")
        
        # Usar nome padrão se não há usuário
        author_name = user.full_name if user else "Usuário Anônimo"
        
        # Criar comentário
        db_comment = TicketService.create_comment(db, comment, ticket_id, author_name)
        return CommentResponse.from_orm(db_comment)

    @staticmethod
    def get_ticket_comments(db: Session, ticket_id: int, user: User) -> List[CommentResponse]:
        """Obtém comentários do ticket"""
        ticket = TicketService.get_ticket_by_id(db, ticket_id)
        if not ticket:
            raise HTTPException(status_code=404, detail="Ticket não encontrado")
        
        # Sem autenticação, permitir acesso aos comentários
        comments = TicketService.get_comments_by_ticket(db, ticket_id)
        return [CommentResponse.from_orm(comment) for comment in comments]

    @staticmethod
    def delete_comment(db: Session, comment_id: int, user: User) -> dict:
        """Deleta comentário"""
        comment = db.query(Comment).filter(Comment.id == comment_id).first()
        if not comment:
            raise HTTPException(status_code=404, detail="Comentário não encontrado")
        
        # Sem autenticação, permitir deleção
        success = TicketService.delete_comment(db, comment_id)
        if not success:
            raise HTTPException(status_code=500, detail="Erro ao deletar comentário")
        
        return {"message": "Comentário deletado com sucesso"}
