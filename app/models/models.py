from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Enum, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

Base = declarative_base()

class PriorityEnum(enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"

class StatusEnum(enum.Enum):
    open = "open"
    pending = "pending"
    in_progress = "in-progress"
    resolved = "resolved"
    closed = "closed"

class RoleEnum(enum.Enum):
    servidor = "servidor"
    technician = "technician"
    admin = "admin"

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True, nullable=True)
    hashed_password = Column(String)
    full_name = Column(String)
    avatar_url = Column(String, nullable=True)
    role = Column(Enum(RoleEnum), default=RoleEnum.servidor)
    is_active = Column(Boolean, default=True)
    is_approved = Column(Boolean, default=False)  # Para aprovação de técnicos
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Campos específicos para técnicos
    employee_id = Column(String, nullable=True)
    department = Column(String, nullable=True)
    specialty = Column(JSON, nullable=True)  # Lista de especialidades
    phone = Column(String, nullable=True)
    emergency_contact = Column(String, nullable=True)
    certifications = Column(Text, nullable=True)
    experience_years = Column(Integer, nullable=True)
    availability = Column(String, nullable=True)
    notes = Column(Text, nullable=True)
    
    # Relacionamento com tickets
    tickets = relationship("Ticket", back_populates="user", foreign_keys="Ticket.user_id")
    assigned_tickets = relationship("Ticket", back_populates="assigned_technician", foreign_keys="Ticket.assigned_technician_id")

class Ticket(Base):
    __tablename__ = "tickets"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    problem_type = Column(String, nullable=False)
    location = Column(String, nullable=False)
    priority = Column(Enum(PriorityEnum), default=PriorityEnum.medium)
    status = Column(Enum(StatusEnum), default=StatusEnum.open)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Campos adicionais para SLA e equipamentos
    equipment_id = Column(String, nullable=True)
    sla_deadline = Column(DateTime, nullable=True)
    estimated_time = Column(Integer, nullable=True)  # em minutos
    attachments = Column(JSON, nullable=True)  # Lista de anexos
    
    # Relacionamento com usuário
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", back_populates="tickets", foreign_keys=[user_id])
    
    # Relacionamento com técnico atribuído
    assigned_technician_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    assigned_technician = relationship("User", back_populates="assigned_tickets", foreign_keys=[assigned_technician_id])
    
    # Relacionamento com comentários e histórico
    comments = relationship("Comment", back_populates="ticket", cascade="all, delete-orphan")
    history = relationship("TicketHistory", back_populates="ticket", cascade="all, delete-orphan")

class Comment(Base):
    __tablename__ = "comments"
    
    id = Column(Integer, primary_key=True, index=True)
    text = Column(Text, nullable=False)
    author = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_technical = Column(Integer, default=0)  # 0 = usuário, 1 = técnico (mantido como Integer para compatibilidade)
    
    # Relacionamento com ticket
    ticket_id = Column(Integer, ForeignKey("tickets.id"))
    ticket = relationship("Ticket", back_populates="comments")

class TicketHistory(Base):
    __tablename__ = "ticket_history"
    
    id = Column(Integer, primary_key=True, index=True)
    action = Column(String, nullable=False)  # created, assigned, status_change, note, etc.
    description = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    technician_name = Column(String, nullable=False)
    time_spent = Column(Integer, nullable=True)  # em minutos
    
    # Relacionamento com ticket
    ticket_id = Column(Integer, ForeignKey("tickets.id"))
    ticket = relationship("Ticket", back_populates="history")
