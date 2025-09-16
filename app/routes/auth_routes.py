from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.dependencies import get_db, get_current_user
from app.controllers import AuthController
from app.models import User
from app.schemas import UserCreate, UserLogin, TechRegister, UserResponse

router = APIRouter(tags=["Authentication"])

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user: UserCreate, db: Session = Depends(get_db)):
    """Registro de usuários comuns"""
    return AuthController.register_user(db, user)

@router.post("/tech-register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_technician(tech: TechRegister, db: Session = Depends(get_db)):
    """Registro de técnicos"""
    return AuthController.register_technician(db, tech)

@router.post("/login", include_in_schema=True)
def login(user: UserLogin, db: Session = Depends(get_db)):
    """Login de usuários"""
    return AuthController.login(db, user)

@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """Obter informações do usuário atual"""
    return AuthController.get_current_user_info(current_user)
