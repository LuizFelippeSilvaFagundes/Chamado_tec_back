from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.dependencies import get_db, get_current_user
from app.controllers import UserController
from app.models import User
from app.schemas import UserResponse, UserUpdate
from pydantic import BaseModel
from fastapi import UploadFile, File

class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/profile", response_model=UserResponse)
def get_profile(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Obter perfil do usuário"""
    return UserController.get_user_profile(db, current_user)

@router.put("/profile", response_model=UserResponse)
def update_profile(user_update: UserUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Atualizar perfil do usuário"""
    return UserController.update_user_profile(db, current_user, user_update)

@router.post("/change-password")
def change_password(payload: ChangePasswordRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Alterar senha do usuário autenticado"""
    return UserController.change_password(db, current_user, payload.current_password, payload.new_password)

@router.post('/profile/avatar', response_model=UserResponse)
def upload_avatar(current_user: User = Depends(get_current_user), db: Session = Depends(get_db), file: UploadFile = File(...)):
    """Atualiza o avatar do usuário (salva caminho e retorna perfil)"""
    return UserController.update_avatar(db, current_user, file)
