from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.dependencies import get_db
from app.controllers import UserController
from app.models import User
from app.schemas import UserResponse, UserUpdate
from typing import List
from app.services.user_service import UserService
from pydantic import BaseModel
from fastapi import UploadFile, File

class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str

router = APIRouter(prefix="/servidores", tags=["Servidores"])

@router.get("/profile")
def get_profile(db: Session = Depends(get_db)):
    """Obter perfil do usuário"""
    return {"message": "Endpoint desabilitado - autenticação removida"}

@router.put("/profile")
def update_profile(user_update: UserUpdate, db: Session = Depends(get_db)):
    """Atualizar perfil do usuário"""
    return {"message": "Endpoint desabilitado - autenticação removida"}

@router.post("/change-password")
def change_password(payload: ChangePasswordRequest, db: Session = Depends(get_db)):
    """Alterar senha do usuário"""
    return {"message": "Endpoint desabilitado - autenticação removida"}

@router.post('/profile/avatar')
def upload_avatar(db: Session = Depends(get_db), file: UploadFile = File(...)):
    """Atualiza o avatar do usuário"""
    return {"message": "Endpoint desabilitado - autenticação removida"}

@router.get("/todos", response_model=List[UserResponse])
def list_all_users(db: Session = Depends(get_db)):
    """Lista usuários de todas as áreas (servidores, técnicos e admins) visível a qualquer usuário autenticado"""
    users = UserService.get_users_by_role(db, "servidor") + UserService.get_users_by_role(db, "technician") + UserService.get_users_by_role(db, "admin")
    return [UserResponse.from_orm(u) for u in users]
