from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from models import User, Ticket, Comment, TicketHistory
from schemas import UserCreate, TicketCreate, CommentCreate, TicketHistoryCreate
from auth import get_password_hash
from datetime import datetime, timedelta
from typing import List, Optional

# Funções de Usuário
def create_user(db: Session, user: UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = User(
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        hashed_password=hashed_password,
        role=user.role,
        is_active=True,
        is_approved=True if user.role == "user" else False,  # Usuários normais são aprovados automaticamente
        # Campos específicos de técnico
        employee_id=user.employee_id,
        department=user.department,
        specialty=user.specialty,
        phone=user.phone,
        emergency_contact=user.emergency_contact,
        certifications=user.certifications,
        experience_years=user.experience_years,
        availability=user.availability,
        notes=user.notes
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()

    

def get_user_by_id(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()

def get_users_by_role(db: Session, role: str, skip: int = 0, limit: int = 100):
    return db.query(User).filter(User.role == role).offset(skip).limit(limit).all()

def get_pending_technicians(db: Session):
    return db.query(User).filter(
        and_(User.role == "technician", User.is_approved == False)
    ).all()

def approve_technician(db: Session, technician_id: int):
    technician = get_user_by_id(db, technician_id)
    if technician and technician.role == "technician":
        technician.is_approved = True
        db.commit()
        db.refresh(technician)
    return technician

def update_user(db: Session, user_id: int, user_update: dict):
    db_user = get_user_by_id(db, user_id)
    if db_user:
        for field, value in user_update.items():
            if value is not None:
                setattr(db_user, field, value)
        db.commit()
        db.refresh(db_user)
    return db_user

# Funções de Ticket
def create_ticket(db: Session, ticket: TicketCreate, user_id: int):
    db_ticket = Ticket(
        **ticket.dict(),
        user_id=user_id
    )
    db.add(db_ticket)
    db.commit()
    db.refresh(db_ticket)
    return db_ticket

def get_tickets_by_user(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    return db.query(Ticket).filter(Ticket.user_id == user_id).offset(skip).limit(limit).all()

def get_tickets_by_technician(db: Session, technician_id: int, skip: int = 0, limit: int = 100):
    return db.query(Ticket).filter(Ticket.assigned_technician_id == technician_id).offset(skip).limit(limit).all()

def get_all_tickets(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Ticket).offset(skip).limit(limit).all()

def get_tickets_by_status(db: Session, status: str, skip: int = 0, limit: int = 100):
    return db.query(Ticket).filter(Ticket.status == status).offset(skip).limit(limit).all()

def assign_ticket_to_technician(db: Session, ticket_id: int, technician_id: int):
    ticket = get_ticket_by_id(db, ticket_id)
    if ticket:
        ticket.assigned_technician_id = technician_id
        ticket.status = "in-progress"
        db.commit()
        db.refresh(ticket)
        
        # Adicionar ao histórico
        create_ticket_history(db, TicketHistoryCreate(
            action="assigned",
            description=f"Ticket atribuído ao técnico ID {technician_id}"
        ), ticket_id, "Sistema")
    return ticket

def get_ticket_by_id(db: Session, ticket_id: int):
    return db.query(Ticket).filter(Ticket.id == ticket_id).first()

def update_ticket(db: Session, ticket_id: int, ticket_update: dict):
    db_ticket = get_ticket_by_id(db, ticket_id)
    if db_ticket:
        for field, value in ticket_update.items():
            if value is not None:
                setattr(db_ticket, field, value)
        db_ticket.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(db_ticket)
    return db_ticket

def delete_ticket(db: Session, ticket_id: int):
    db_ticket = get_ticket_by_id(db, ticket_id)
    if db_ticket:
        db.delete(db_ticket)
        db.commit()
        return True
    return False

# Funções de Comentário
def create_comment(db: Session, comment: CommentCreate, ticket_id: int, author: str):
    db_comment = Comment(
        **comment.dict(),
        ticket_id=ticket_id,
        author=author
    )
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return db_comment

def get_comments_by_ticket(db: Session, ticket_id: int):
    return db.query(Comment).filter(Comment.ticket_id == ticket_id).order_by(Comment.created_at).all()

def delete_comment(db: Session, comment_id: int):
    db_comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if db_comment:
        db.delete(db_comment)
        db.commit()
        return True
    return False

# Funções de Histórico de Ticket
def create_ticket_history(db: Session, history: TicketHistoryCreate, ticket_id: int, technician_name: str):
    db_history = TicketHistory(
        **history.dict(),
        ticket_id=ticket_id,
        technician_name=technician_name
    )
    db.add(db_history)
    db.commit()
    db.refresh(db_history)
    return db_history

def get_ticket_history(db: Session, ticket_id: int):
    return db.query(TicketHistory).filter(TicketHistory.ticket_id == ticket_id).order_by(TicketHistory.timestamp).all()

# Funções de Estatísticas para Dashboard
def get_tech_dashboard_stats(db: Session, technician_id: int):
    total_tickets = db.query(Ticket).filter(Ticket.assigned_technician_id == technician_id).count()
    pending_tickets = db.query(Ticket).filter(
        and_(Ticket.assigned_technician_id == technician_id, Ticket.status == "pending")
    ).count()
    in_progress_tickets = db.query(Ticket).filter(
        and_(Ticket.assigned_technician_id == technician_id, Ticket.status == "in-progress")
    ).count()
    resolved_tickets = db.query(Ticket).filter(
        and_(Ticket.assigned_technician_id == technician_id, Ticket.status == "resolved")
    ).count()
    
    # Tickets em atraso (SLA vencido)
    overdue_tickets = db.query(Ticket).filter(
        and_(
            Ticket.assigned_technician_id == technician_id,
            Ticket.sla_deadline < datetime.utcnow(),
            Ticket.status.in_(["pending", "in-progress"])
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
