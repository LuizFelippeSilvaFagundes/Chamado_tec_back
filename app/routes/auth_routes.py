from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.dependencies import get_db
from app.controllers import AuthController
from app.schemas import ServidorRegister, AdminRegister
from app.models import User
from app.schemas import     UserCreate, UserLogin, TechRegister, UserResponse

router = APIRouter(tags=["Authentication"])

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user: ServidorRegister, db: Session = Depends(get_db)):
    """Registro de servidores (username, full_name, phone, password)"""
    return AuthController.register_servidor(db, user)

@router.post("/tech-register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_technician(tech: TechRegister, db: Session = Depends(get_db)):
    """Registro de técnicos"""
    return AuthController.register_technician(db, tech)

@router.post("/admin-register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_admin(admin: AdminRegister, db: Session = Depends(get_db)):
    """Registro de administradores"""
    return AuthController.register_admin(db, admin)

@router.post("/login", include_in_schema=True)
def login(user: UserLogin, db: Session = Depends(get_db)):
    """Login de usuários"""
    return AuthController.login(db, user)

@router.get("/me")
def get_me(username: str = None, db: Session = Depends(get_db)):
    """Obter informações do usuário atual"""
    if username:
        from app.services.user_service import UserService
        user = UserService.get_user_by_username(db, username)
        if user:
            from app.schemas import UserResponse
            return UserResponse.from_orm(user)
        else:
            from fastapi import HTTPException
            raise HTTPException(status_code=404, detail="Usuário não encontrado")
    else:
        return {"message": "Username é obrigatório"}
