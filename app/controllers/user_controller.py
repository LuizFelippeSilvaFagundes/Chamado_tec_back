from typing import List
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.services.user_service import UserService
from app.models import User
from schemas import UserResponse, UserUpdate

class UserController:
    @staticmethod
    def get_user_profile(db: Session, user: User) -> UserResponse:
        """Obtém perfil do usuário atual"""
        # Recarregar dados do banco para garantir atualização
        fresh_user = UserService.get_user_by_id(db, user.id)
        if not fresh_user:
            raise HTTPException(status_code=404, detail="Usuário não encontrado")
        return UserResponse.from_orm(fresh_user)

    @staticmethod
    def update_user_profile(db: Session, user: User, user_update: UserUpdate) -> UserResponse:
        """Atualiza perfil do usuário"""
        updated_user = UserService.update_user(db, user.id, user_update)
        if not updated_user:
            raise HTTPException(status_code=404, detail="Usuário não encontrado")
        return UserResponse.from_orm(updated_user)