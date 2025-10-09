"""
Rotas para gerenciamento de avatares
"""
from fastapi import APIRouter, Depends, File, UploadFile, HTTPException
from sqlalchemy.orm import Session
from app.dependencies import get_db, get_current_user
from app.controllers import avatar_controller
from app.models import User

router = APIRouter(prefix="/avatars", tags=["Avatars"])


@router.post("/upload")
async def upload_avatar(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload de avatar para o usuário logado
    
    - **file**: Arquivo de imagem (JPG, PNG, GIF, WEBP)
    - Tamanho máximo: 5MB
    """
    return avatar_controller.upload_avatar(current_user.id, file, db)


@router.post("/{user_id}/upload")
async def upload_avatar_by_id(
    user_id: int,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload de avatar para um usuário específico (Admin/Próprio usuário)
    
    - **user_id**: ID do usuário
    - **file**: Arquivo de imagem
    """
    # Verificar permissão: só admin ou o próprio usuário pode fazer upload
    if current_user.role.value != "admin" and current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Sem permissão para alterar avatar deste usuário")
    
    return avatar_controller.upload_avatar(user_id, file, db)


@router.get("/me")
async def get_my_avatar(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obter informações do avatar do usuário logado
    """
    return avatar_controller.get_avatar(current_user.id, db)


@router.get("/{user_id}")
async def get_user_avatar(
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    Obter informações do avatar de um usuário específico
    """
    return avatar_controller.get_avatar(user_id, db)


@router.delete("/me")
async def delete_my_avatar(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Deletar avatar do usuário logado
    """
    return avatar_controller.delete_avatar(current_user.id, db)


@router.delete("/{user_id}")
async def delete_user_avatar(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Deletar avatar de um usuário específico (Admin/Próprio usuário)
    """
    # Verificar permissão
    if current_user.role.value != "admin" and current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Sem permissão para deletar avatar deste usuário")
    
    return avatar_controller.delete_avatar(user_id, db)


@router.get("/")
async def list_user_avatars(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Listar todos os usuários com informações de avatar (Admin apenas)
    """
    if current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Acesso restrito a administradores")
    
    return avatar_controller.get_user_avatars_list(db, skip, limit)

