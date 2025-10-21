from datetime import datetime, timedelta
from typing import Optional
from jose import jwt, JWTError
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from app.models import User

# Configurações
SECRET_KEY = "minha_chave_super_secreta_1234567890"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthService:
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verifica se a senha plana corresponde ao hash"""
        # Bcrypt tem limite de 72 bytes - truncar se necessário
        if len(plain_password.encode('utf-8')) > 72:
            plain_password = plain_password[:72]
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def get_password_hash(password: str) -> str:
        """Gera hash da senha"""
        # Bcrypt tem limite de 72 bytes - truncar se necessário
        if len(password.encode('utf-8')) > 72:
            password = password[:72]
        return pwd_context.hash(password)

    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Cria token JWT de acesso"""
        to_encode = data.copy()
        expire = datetime.utcnow() + (expires_delta if expires_delta else timedelta(minutes=15))
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    @staticmethod
    def decode_token(token: str) -> dict:
        """Decodifica token JWT"""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload
        except JWTError:
            return None

    @staticmethod
    def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
        """Autentica usuário por username e senha"""
        from app.services.user_service import UserService
        user = UserService.get_user_by_username(db, username)
        if not user:
            return None
        if not AuthService.verify_password(password, user.hashed_password):
            return None
        return user

    @staticmethod
    def get_current_user_from_token(db: Session, token: str) -> Optional[User]:
        """Obtém usuário atual a partir do token"""
        payload = AuthService.decode_token(token)
        if not payload:
            return None
        
        username: str = payload.get("sub")
        user_id: int = payload.get("user_id")
        if username is None or user_id is None:
            return None

        from app.services.user_service import UserService
        user = UserService.get_user_by_id(db, user_id)
        if user is None:
            return None
        
        # Verificar se o usuário está ativo
        if not user.is_active:
            return None
        
        # Verificar se técnicos estão aprovados
        role_str = str(user.role.value) if hasattr(user.role, 'value') else str(user.role)
        if role_str == "technician" and not user.is_approved:
            return None
        
        return user
