from pydantic import BaseModel, field_validator
from email_validator import validate_email, EmailNotValidError
from typing import Optional, List, Union
from datetime import datetime
from enum import Enum

class PriorityEnum(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"

class StatusEnum(str, Enum):
    open = "open"
    pending = "pending"
    in_progress = "in-progress"
    resolved = "resolved"
    closed = "closed"

class RoleEnum(str, Enum):
    servidor = "servidor"
    technician = "technician"
    admin = "admin"

# Schemas de Usuário
class UserBase(BaseModel):
    username: str
    email: Optional[str] = None
    full_name: str

    @field_validator("email")
    @classmethod
    def validate_email_relaxed(cls, value: Optional[str]) -> Optional[str]:
        # Permite omitir email na criação e atualização.
        if value is None or value == "":
            return None
        try:
            result = validate_email(value, check_deliverability=False)
            return result.normalized
        except EmailNotValidError as exc:
            raise ValueError(str(exc))

class UserCreate(UserBase):
    password: str
    role: RoleEnum = RoleEnum.servidor
    # Campos opcionais para técnicos
    employee_id: Optional[str] = None
    department: Optional[str] = None
    specialty: Optional[List[str]] = None
    phone: Optional[str] = None
    emergency_contact: Optional[str] = None
    certifications: Optional[str] = None
    experience_years: Optional[int] = None
    availability: Optional[str] = None
    notes: Optional[str] = None

class TechRegister(UserBase):
    password: str
    role: RoleEnum = RoleEnum.technician
    employee_id: str
    department: str
    specialty: List[str]
    phone: str
    emergency_contact: Optional[str] = None
    certifications: Optional[str] = None
    experience_years: Optional[int] = None
    availability: str = "full-time"
    notes: Optional[str] = None

class ServidorRegister(BaseModel):
    username: str
    full_name: str
    phone: str
    password: str

class AdminRegister(BaseModel):
    username: str
    email: str
    full_name: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(UserBase):
    id: int
    role: RoleEnum
    is_active: bool
    is_approved: bool
    created_at: datetime
    avatar_url: Optional[str] = None
    # Campos específicos de técnico
    employee_id: Optional[str] = None
    department: Optional[str] = None
    specialty: Optional[List[str]] = None
    phone: Optional[str] = None
    emergency_contact: Optional[str] = None
    certifications: Optional[str] = None
    experience_years: Optional[int] = None
    availability: Optional[str] = None
    notes: Optional[str] = None
    
    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    emergency_contact: Optional[str] = None
    certifications: Optional[str] = None
    experience_years: Optional[int] = None
    availability: Optional[str] = None
    notes: Optional[str] = None
    specialty: Optional[List[str]] = None
    is_active: Optional[bool] = None
    is_approved: Optional[bool] = None

    @field_validator("email")
    @classmethod
    def validate_email_relaxed_optional(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        try:
            result = validate_email(value, check_deliverability=False)
            return result.normalized
        except EmailNotValidError as exc:
            raise ValueError(str(exc))

# Schema de Anexo
class AttachmentInfo(BaseModel):
    filename: str
    stored_filename: str
    url: str
    size: int
    type: str

# Schemas de Ticket
class TicketBase(BaseModel):
    title: str
    description: str
    problem_type: str
    location: str
    priority: PriorityEnum = PriorityEnum.medium
    equipment_id: Optional[str] = None
    estimated_time: Optional[int] = None
    attachments: Optional[List[AttachmentInfo]] = None

class TicketCreate(TicketBase):
    pass

class TicketUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    problem_type: Optional[str] = None
    location: Optional[str] = None
    priority: Optional[PriorityEnum] = None
    status: Optional[StatusEnum] = None
    equipment_id: Optional[str] = None
    estimated_time: Optional[int] = None
    assigned_technician_id: Optional[int] = None
    sla_deadline: Optional[datetime] = None

class TicketResponse(TicketBase):
    id: int
    status: StatusEnum
    created_at: datetime
    updated_at: datetime
    user_id: int
    user: UserResponse
    assigned_technician_id: Optional[int] = None
    assigned_technician: Optional[UserResponse] = None
    sla_deadline: Optional[datetime] = None
    assigned_by_admin: Optional[bool] = False
    
    class Config:
        from_attributes = True

# Schemas de Comentário
class CommentBase(BaseModel):
    text: str
    is_technical: bool = False

class CommentCreate(CommentBase):
    pass

class CommentResponse(CommentBase):
    id: int
    author: str
    created_at: datetime
    ticket_id: int
    
    class Config:
        from_attributes = True

# Schemas de Histórico de Ticket
class TicketHistoryBase(BaseModel):
    action: str
    description: str
    time_spent: Optional[int] = None

class TicketHistoryCreate(TicketHistoryBase):
    pass

class TicketHistoryResponse(TicketHistoryBase):
    id: int
    timestamp: datetime
    technician_name: str
    ticket_id: int
    
    class Config:
        from_attributes = True

# Schemas para Dashboard de Técnico
class TechDashboardStats(BaseModel):
    total_tickets: int
    pending_tickets: int
    in_progress_tickets: int
    resolved_tickets: int
    overdue_tickets: int
    avg_resolution_time: float

class TicketWithHistory(TicketResponse):
    history: List[TicketHistoryResponse] = []
    comments: List[CommentResponse] = []

# Schema completo de Ticket com comentários
class TicketWithComments(TicketResponse):
    comments: List[CommentResponse] = []
