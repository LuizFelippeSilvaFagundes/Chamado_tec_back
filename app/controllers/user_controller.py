from typing import List
from fastapi import HTTPException, UploadFile
from sqlalchemy.orm import Session
from app.services.user_service import UserService
from app.models import User
from app.schemas import UserResponse, UserUpdate
from app.services.auth_service import AuthService
import os
from uuid import uuid4

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

    @staticmethod
    def change_password(db: Session, user: User, current_password: str, new_password: str):
        """Altera a senha do usuário após validar a senha atual"""
        if not AuthService.verify_password(current_password, user.hashed_password):
            raise HTTPException(status_code=400, detail="Senha atual incorreta")

        new_hash = AuthService.get_password_hash(new_password)
        updated = UserService.update_user_password(db, user.id, new_hash)
        if not updated:
            raise HTTPException(status_code=404, detail="Usuário não encontrado")
        return {"detail": "Senha alterada com sucesso"}

    @staticmethod
    def update_avatar(db: Session, user: User, file: UploadFile) -> UserResponse:
        """Salva upload do avatar em /static/avatars e atualiza avatar_url"""
        ext = os.path.splitext(file.filename)[1].lower()
        if ext not in ['.png', '.jpg', '.jpeg', '.webp']:
            raise HTTPException(status_code=400, detail="Formato de imagem inválido")
        avatars_dir = os.path.abspath(os.path.join(os.getcwd(), 'static', 'avatars'))
        os.makedirs(avatars_dir, exist_ok=True)
        filename = f"{uuid4().hex}{ext}"
        path = os.path.join(avatars_dir, filename)
        with open(path, 'wb') as f:
            f.write(file.file.read())
        # salvar caminho relativo
        rel_url = f"/static/avatars/{filename}"
        updated_user = UserService.update_user_avatar(db, user.id, rel_url)
        if not updated_user:
            raise HTTPException(status_code=404, detail="Usuário não encontrado")
        return UserResponse.from_orm(updated_user)
