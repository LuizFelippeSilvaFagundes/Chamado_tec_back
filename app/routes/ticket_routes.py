from typing import List, Optional
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.dependencies import get_db
from app.controllers import TicketController
from app.models import User
from app.schemas import (
    TicketCreate, TicketUpdate, TicketResponse, TicketWithComments,
    CommentCreate, CommentResponse
)

class TicketCreateWithUser(TicketCreate):
    username: Optional[str] = None

router = APIRouter(prefix="/tickets", tags=["Tickets"])

@router.post("", response_model=TicketResponse, status_code=status.HTTP_201_CREATED)
def create_ticket(ticket: TicketCreateWithUser, db: Session = Depends(get_db)):
    """Criar novo ticket"""
    from app.services.user_service import UserService
    
    # Se username foi fornecido, buscar o usuário
    user = None
    if ticket.username:
        user = UserService.get_user_by_username(db, ticket.username)
    
    return TicketController.create_ticket(db, ticket, user)

@router.get("/me/{username}", response_model=List[TicketWithComments])
def get_my_tickets_by_username(username: str, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Obter tickets do usuário logado por username"""
    from app.services.user_service import UserService
    user = UserService.get_user_by_username(db, username)
    if not user:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return TicketController.get_user_tickets(db, user, skip, limit)

@router.get("", response_model=List[TicketWithComments])
def get_my_tickets(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Obter meus tickets"""
    return TicketController.get_user_tickets(db, None, skip, limit)

@router.get("/{ticket_id}", response_model=TicketWithComments)
def get_ticket(ticket_id: int, db: Session = Depends(get_db)):
    """Obter detalhes do ticket"""
    return TicketController.get_ticket_details(db, ticket_id, None)

@router.put("/{ticket_id}", response_model=TicketResponse)
def update_ticket(ticket_id: int, ticket_update: TicketUpdate, db: Session = Depends(get_db)):
    """Atualizar ticket"""
    return TicketController.update_ticket(db, ticket_id, ticket_update, None)

@router.delete("/{ticket_id}")
def delete_ticket(ticket_id: int, db: Session = Depends(get_db)):
    """Deletar ticket"""
    return TicketController.delete_ticket(db, ticket_id, None)

# Rotas para comentários
@router.post("/{ticket_id}/comments", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
def add_comment(ticket_id: int, comment: CommentCreate, db: Session = Depends(get_db)):
    """Adicionar comentário ao ticket"""
    return TicketController.add_comment(db, ticket_id, comment, None)

@router.get("/{ticket_id}/comments", response_model=List[CommentResponse])
def get_ticket_comments(ticket_id: int, db: Session = Depends(get_db)):
    """Obter comentários do ticket"""
    return TicketController.get_ticket_comments(db, ticket_id, None)

@router.delete("/comments/{comment_id}")
def delete_comment(comment_id: int, db: Session = Depends(get_db)):
    """Deletar comentário"""
    return TicketController.delete_comment(db, comment_id, None)
