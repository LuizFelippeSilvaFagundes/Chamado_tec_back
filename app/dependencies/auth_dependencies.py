from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.dependencies.database import get_db
from app.services.auth_service import AuthService
from app.services.user_service import UserService
from app.models import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    """Dependência para obter usuário atual a partir do token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token inválido ou expirado",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    user = AuthService.get_current_user_from_token(db, token)
    if user is None:
        raise credentials_exception
    
    # Verificar se o usuário está ativo
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuário inativo"
        )
    
    # Verificar se técnicos estão aprovados
    if user.role == "technician" and not user.is_approved:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Técnico aguardando aprovação"
        )
    
    return user

def require_technician_or_admin(current_user: User = Depends(get_current_user)) -> User:
    """Dependência que requer usuário técnico ou admin"""
    if not UserService.is_technician_or_admin(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Acesso negado. Apenas técnicos e administradores."
        )
    return current_user

def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """Dependência que requer usuário admin"""
    if not UserService.is_admin(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado. Apenas administradores."
        )
    return current_user