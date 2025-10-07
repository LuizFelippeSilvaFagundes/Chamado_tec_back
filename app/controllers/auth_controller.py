from datetime import timedelta
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.services.auth_service import AuthService, ACCESS_TOKEN_EXPIRE_MINUTES
from app.services.user_service import UserService
from app.schemas import UserLogin, UserCreate, TechRegister, UserResponse, ServidorRegister, RoleEnum

class AuthController:
    @staticmethod
    def register_user(db: Session, user: UserCreate) -> UserResponse:
        """Registra um novo usuário"""
        # Verificar se usuário já existe
        exists, error_msg = UserService.check_user_exists(db, user.username, user.email)
        if exists:
            raise HTTPException(status_code=400, detail=error_msg)
        
        # Criar usuário
        db_user = UserService.create_user(db, user)
        return UserResponse.from_orm(db_user)

    @staticmethod
    def register_servidor(db: Session, payload: ServidorRegister) -> UserResponse:
        """Registra um novo servidor com campos mínimos"""
        # Verificar existência por username (email é opcional)
        exists, error_msg = UserService.check_user_exists(db, payload.username, None)
        if exists:
            raise HTTPException(status_code=400, detail=error_msg)

        user_data = UserCreate(
            username=payload.username,
            email=None,
            full_name=payload.full_name,
            password=payload.password,
            role=RoleEnum.servidor,
            phone=payload.phone,
        )
        db_user = UserService.create_user(db, user_data)
        return UserResponse.from_orm(db_user)

    @staticmethod
    def register_technician(db: Session, tech: TechRegister) -> UserResponse:
        """Registra um novo técnico"""
        # Verificar se usuário já existe
        exists, error_msg = UserService.check_user_exists(db, tech.username, tech.email)
        if exists:
            raise HTTPException(status_code=400, detail=error_msg)
        
        # Converter TechRegister para UserCreate
        user_data = UserCreate(
            username=tech.username,
            email=tech.email,
            full_name=tech.full_name,
            password=tech.password,
            role=tech.role,
            employee_id=tech.employee_id,
            department=tech.department,
            specialty=tech.specialty,
            phone=tech.phone,
            emergency_contact=tech.emergency_contact,
            certifications=tech.certifications,
            experience_years=tech.experience_years,
            availability=tech.availability,
            notes=tech.notes
        )
        
        # Criar usuário
        db_user = UserService.create_user(db, user_data)
        return UserResponse.from_orm(db_user)

    @staticmethod
    def login(db: Session, user_login: UserLogin) -> dict:
        """Realiza login e retorna token"""
        # Autenticar usuário
        user = AuthService.authenticate_user(db, user_login.username, user_login.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuário ou senha incorretos"
            )
        
        # Criar token
        token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        token = AuthService.create_access_token(
            data={"sub": user.username, "user_id": user.id}, 
            expires_delta=token_expires
        )
        
        return {
            "access_token": token,
            "token_type": "bearer",
            "user": UserResponse.from_orm(user)
        }

    @staticmethod
    def get_current_user_info(user) -> UserResponse:
        """Retorna informações do usuário atual"""
        return UserResponse.from_orm(user)
