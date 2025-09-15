from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from database import Base, engine, SessionLocal
from schemas import (
    UserCreate, UserLogin, UserResponse, UserUpdate, TechRegister,
    TicketCreate, TicketResponse, TicketUpdate, TicketWithComments, TicketWithHistory,
    CommentCreate, CommentResponse,
    TicketHistoryCreate, TicketHistoryResponse,
    TechDashboardStats, RoleEnum
)
from crud import (
    create_user, get_user_by_username, get_user_by_id, update_user,
    get_users_by_role, get_pending_technicians, approve_technician,
    create_ticket, get_tickets_by_user, get_ticket_by_id, 
    get_tickets_by_technician, get_all_tickets, get_tickets_by_status,
    assign_ticket_to_technician, update_ticket, delete_ticket,
    create_comment, get_comments_by_ticket, delete_comment,
    create_ticket_history, get_ticket_history, get_tech_dashboard_stats
)
from auth import verify_password,       create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES, get_current_user

from datetime import timedelta
from typing import List
from models import User, Comment

# === CRIAÇÃO AUTOMÁTICA DO BANCO E TABELAS ===
def init_db():
    # Cria todas as tabelas se não existirem
    Base.metadata.create_all(bind=engine)

# Inicializa o banco ao iniciar o app
init_db()

app = FastAPI(title="Sistema de Tickets - Prefeitura", version="1.0.0")

# Configuração de CORS
origins = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependência do DB
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ---------------- ROTAS ---------------- #

# Registro de Usuários
@app.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user: UserCreate, db: Session = Depends(get_db)):
    db_user = get_user_by_username(db, user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Usuário já existe")
    
    db_user_email = db.query(User).filter(User.email == user.email).first()
    if db_user_email:
        raise HTTPException(status_code=400, detail="Email já cadastrado")
    
    return create_user(db, user)

# Registro de Técnicos
@app.post("/tech-register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_technician(tech: TechRegister, db: Session = Depends(get_db)):
    db_user = get_user_by_username(db, tech.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Usuário já existe")
    
    db_user_email = db.query(User).filter(User.email == tech.email).first()
    if db_user_email:
        raise HTTPException(status_code=400, detail="Email já cadastrado")
    
    # Converter TechRegister para UserCreate
    user_data = UserCreate(
        username=tech.username,
        email=tech.email,
        full_name=tech.full_name,
        password=tech.password,
        role=tech.role,
        employee_id=tech.employee_id,
        department=tech.department,
        specialty=tech.specialty,
        phone=tech.phone,
        emergency_contact=tech.emergency_contact,
        certifications=tech.certifications,
        experience_years=tech.experience_years,
        availability=tech.availability,
        notes=tech.notes
    )
    
    return create_user(db, user_data)

# Login
@app.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = get_user_by_username(db, user.username)
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Usuário ou senha incorretos")
    
    token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    token = create_access_token(data={"sub": db_user.username, "user_id": db_user.id}, expires_delta=token_expires)
    return {"access_token": token, "token_type": "bearer", "user": UserResponse.from_orm(db_user)}

@app.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == current_user.id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return user

# Função auxiliar para verificar se é técnico ou admin
def require_technician_or_admin(current_user: User = Depends(get_current_user)):
    if current_user.role not in ["technician", "admin"]:
        raise HTTPException(status_code=403, detail="Acesso negado. Apenas técnicos e administradores.")
    return current_user

def require_admin(current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Acesso negado. Apenas administradores.")
    return current_user

# Rotas para Técnicos
@app.get("/tech/dashboard/stats", response_model=TechDashboardStats)
def get_tech_dashboard_stats_endpoint(
    current_user: User = Depends(require_technician_or_admin),
    db: Session = Depends(get_db)
):
    return get_tech_dashboard_stats(db, current_user.id)

@app.get("/tech/tickets", response_model=List[TicketResponse])
def get_tech_tickets(
    skip: int = 0, 
    limit: int = 100,
    current_user: User = Depends(require_technician_or_admin),
    db: Session = Depends(get_db)
):
    return get_tickets_by_technician(db, current_user.id, skip, limit)

@app.get("/tech/tickets/{ticket_id}", response_model=TicketWithHistory)
def get_tech_ticket_details(
    ticket_id: int,
    current_user: User = Depends(require_technician_or_admin),
    db: Session = Depends(get_db)
):
    ticket = get_ticket_by_id(db, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket não encontrado")
    
    # Verificar se o técnico tem acesso ao ticket
    if ticket.assigned_technician_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Acesso negado")
    
    return ticket

@app.put("/tech/tickets/{ticket_id}/status", response_model=TicketResponse)
def update_ticket_status(
    ticket_id: int,
    status_update: dict,
    current_user: User = Depends(require_technician_or_admin),
    db: Session = Depends(get_db)
):
    ticket = get_ticket_by_id(db, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket não encontrado")
    
    if ticket.assigned_technician_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Acesso negado")
    
    # Atualizar status
    updated_ticket = update_ticket(db, ticket_id, status_update)
    
    # Adicionar ao histórico
    create_ticket_history(db, TicketHistoryCreate(
        action="status_change",
        description=f"Status alterado para {status_update.get('status', 'N/A')}"
    ), ticket_id, current_user.full_name)
    
    return updated_ticket

@app.post("/tech/tickets/{ticket_id}/history", response_model=TicketHistoryResponse)
def add_ticket_history(
    ticket_id: int,
    history: TicketHistoryCreate,
    current_user: User = Depends(require_technician_or_admin),
    db: Session = Depends(get_db)
):
    ticket = get_ticket_by_id(db, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket não encontrado")
    
    if ticket.assigned_technician_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Acesso negado")
    
    return create_ticket_history(db, history, ticket_id, current_user.full_name)

# Rotas para Administradores
@app.get("/admin/technicians/pending", response_model=List[UserResponse])
def get_pending_technicians_endpoint(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    return get_pending_technicians(db)

@app.post("/admin/technicians/{technician_id}/approve", response_model=UserResponse)
def approve_technician_endpoint(
    technician_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    technician = approve_technician(db, technician_id)
    if not technician:
        raise HTTPException(status_code=404, detail="Técnico não encontrado")
    return technician

@app.get("/admin/tickets", response_model=List[TicketResponse])
def get_all_tickets_admin(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    return get_all_tickets(db, skip, limit)

@app.post("/admin/tickets/{ticket_id}/assign/{technician_id}", response_model=TicketResponse)
def assign_ticket_admin(
    ticket_id: int,
    technician_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    return assign_ticket_to_technician(db, ticket_id, technician_id)

# Tickets
@app.post("/tickets", response_model=TicketResponse, status_code=status.HTTP_201_CREATED)
def create_new_ticket(ticket: TicketCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return create_ticket(db, ticket, current_user.id)

@app.get("/tickets", response_model=List[TicketWithComments])
def get_my_tickets(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return get_tickets_by_user(db, current_user.id, skip, limit)

@app.get("/tickets/{ticket_id}", response_model=TicketWithComments)
def get_ticket(ticket_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    ticket = get_ticket_by_id(db, ticket_id)
    if not ticket or ticket.user_id != current_user.id:
        raise HTTPException(status_code=404 if not ticket else 403, detail="Ticket não encontrado ou acesso negado")
    return ticket

@app.put("/tickets/{ticket_id}", response_model=TicketResponse)
def update_ticket_status(ticket_id: int, ticket_update: TicketUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    ticket = get_ticket_by_id(db, ticket_id)
    if not ticket or ticket.user_id != current_user.id:
        raise HTTPException(status_code=404 if not ticket else 403, detail="Ticket não encontrado ou acesso negado")
    return update_ticket(db, ticket_id, ticket_update.dict(exclude_unset=True))

@app.delete("/tickets/{ticket_id}")
def delete_user_ticket(ticket_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    ticket = get_ticket_by_id(db, ticket_id)
    if not ticket or ticket.user_id != current_user.id:
        raise HTTPException(status_code=404 if not ticket else 403, detail="Ticket não encontrado ou acesso negado")
    if delete_ticket(db, ticket_id):
        return {"message": "Ticket deletado com sucesso"}
    raise HTTPException(status_code=500, detail="Erro ao deletar ticket")

# Comentários
@app.post("/tickets/{ticket_id}/comments", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
def add_comment(ticket_id: int, comment: CommentCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    ticket = get_ticket_by_id(db, ticket_id)
    if not ticket or ticket.user_id != current_user.id:
        raise HTTPException(status_code=404 if not ticket else 403, detail="Ticket não encontrado ou acesso negado")
    return create_comment(db, comment, ticket_id, current_user.full_name)

@app.get("/tickets/{ticket_id}/comments", response_model=List[CommentResponse])
def get_ticket_comments(ticket_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    ticket = get_ticket_by_id(db, ticket_id)
    if not ticket or ticket.user_id != current_user.id:
        raise HTTPException(status_code=404 if not ticket else 403, detail="Ticket não encontrado ou acesso negado")
    return get_comments_by_ticket(db, ticket_id)

@app.delete("/comments/{comment_id}")
def delete_user_comment(comment_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="Comentário não encontrado")
    ticket = get_ticket_by_id(db, comment.ticket_id)
    if ticket.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Acesso negado")
    if delete_comment(db, comment_id):
        return {"message": "Comentário deletado com sucesso"}
    raise HTTPException(status_code=500, detail="Erro ao deletar comentário")

# Rodar servidor diretamente
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
