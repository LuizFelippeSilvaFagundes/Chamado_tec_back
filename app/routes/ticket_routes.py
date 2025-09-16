from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.dependencies import get_db, get_current_user
from app.controllers import TicketController
from app.models import User
from app.schemas import (
    TicketCreate, TicketUpdate, TicketResponse, TicketWithComments,
    CommentCreate, CommentResponse
)

router = APIRouter(prefix="/tickets", tags=["Tickets"])

@router.post("", response_model=TicketResponse, status_code=status.HTTP_201_CREATED)
def create_ticket(ticket: TicketCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Criar novo ticket"""
    return TicketController.create_ticket(db, ticket, current_user)

@router.get("", response_model=List[TicketWithComments])
def get_my_tickets(skip: int = 0, limit: int = 100, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Obter meus tickets"""
    return TicketController.get_user_tickets(db, current_user, skip, limit)

@router.get("/{ticket_id}", response_model=TicketWithComments)
def get_ticket(ticket_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Obter detalhes do ticket"""
    return TicketController.get_ticket_details(db, ticket_id, current_user)

@router.put("/{ticket_id}", response_model=TicketResponse)
def update_ticket(ticket_id: int, ticket_update: TicketUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Atualizar ticket"""
    return TicketController.update_ticket(db, ticket_id, ticket_update, current_user)

@router.delete("/{ticket_id}")
def delete_ticket(ticket_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Deletar ticket"""
    return TicketController.delete_ticket(db, ticket_id, current_user)

# Rotas para comentários
@router.post("/{ticket_id}/comments", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
def add_comment(ticket_id: int, comment: CommentCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Adicionar comentário ao ticket"""
    return TicketController.add_comment(db, ticket_id, comment, current_user)

@router.get("/{ticket_id}/comments", response_model=List[CommentResponse])
def get_ticket_comments(ticket_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Obter comentários do ticket"""
    return TicketController.get_ticket_comments(db, ticket_id, current_user)

@router.delete("/comments/{comment_id}")
def delete_comment(comment_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Deletar comentário"""
    return TicketController.delete_comment(db, comment_id, current_user)
