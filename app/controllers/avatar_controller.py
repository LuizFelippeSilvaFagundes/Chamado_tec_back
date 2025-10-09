"""
Controller para gerenciamento de avatares de usuários
"""
from fastapi import UploadFile, HTTPException
from sqlalchemy.orm import Session
from app.models import User
import os
import shutil
from pathlib import Path
from uuid import uuid4


# Diretório para salvar avatares
AVATAR_DIR = Path("static/avatars")
AVATAR_DIR.mkdir(parents=True, exist_ok=True)

# Extensões permitidas
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB


def upload_avatar(user_id: int, file: UploadFile, db: Session):
    """
    Upload de avatar para um usuário
    """
    # Buscar usuário
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    # Validar extensão do arquivo
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400, 
            detail=f"Extensão não permitida. Use: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    # Validar tamanho (se possível)
    if file.size and file.size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail="Arquivo muito grande. Tamanho máximo: 5MB"
        )
    
    # Deletar avatar antigo se existir
    if user.avatar_url:
        delete_avatar_file(user.avatar_url)
    
    # Gerar nome único para o arquivo
    unique_filename = f"{uuid4()}{file_ext}"
    file_path = AVATAR_DIR / unique_filename
    
    # Salvar arquivo
    try:
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao salvar arquivo: {str(e)}")
    
    # Atualizar URL do avatar no banco
    avatar_url = f"/static/avatars/{unique_filename}"
    user.avatar_url = avatar_url
    db.commit()
    db.refresh(user)
    
    return {
        "message": "Avatar atualizado com sucesso",
        "avatar_url": avatar_url,
        "user": {
            "id": user.id,
            "username": user.username,
            "full_name": user.full_name,
            "avatar_url": user.avatar_url
        }
    }


def get_avatar(user_id: int, db: Session):
    """
    Obter informações do avatar de um usuário
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    if not user.avatar_url:
        raise HTTPException(status_code=404, detail="Usuário não possui avatar")
    
    # Verificar se o arquivo existe
    avatar_path = Path(user.avatar_url.lstrip("/"))
    if not avatar_path.exists():
        # Limpar URL do banco se arquivo não existe
        user.avatar_url = None
        db.commit()
        raise HTTPException(status_code=404, detail="Arquivo de avatar não encontrado")
    
    return {
        "user_id": user.id,
        "username": user.username,
        "avatar_url": user.avatar_url,
        "file_size": avatar_path.stat().st_size,
        "file_exists": True
    }


def delete_avatar(user_id: int, db: Session):
    """
    Deletar avatar de um usuário
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    if not user.avatar_url:
        raise HTTPException(status_code=404, detail="Usuário não possui avatar")
    
    # Deletar arquivo físico
    deleted = delete_avatar_file(user.avatar_url)
    
    # Remover URL do banco
    user.avatar_url = None
    db.commit()
    db.refresh(user)
    
    return {
        "message": "Avatar deletado com sucesso",
        "file_deleted": deleted,
        "user": {
            "id": user.id,
            "username": user.username,
            "avatar_url": None
        }
    }


def delete_avatar_file(avatar_url: str) -> bool:
    """
    Helper para deletar arquivo físico do avatar
    """
    try:
        avatar_path = Path(avatar_url.lstrip("/"))
        if avatar_path.exists():
            avatar_path.unlink()
            return True
        return False
    except Exception as e:
        print(f"Erro ao deletar arquivo: {e}")
        return False


def get_user_avatars_list(db: Session, skip: int = 0, limit: int = 100):
    """
    Listar todos os usuários com seus avatares
    """
    users = db.query(User).offset(skip).limit(limit).all()
    
    return [
        {
            "id": user.id,
            "username": user.username,
            "full_name": user.full_name,
            "avatar_url": user.avatar_url,
            "has_avatar": user.avatar_url is not None
        }
        for user in users
    ]

