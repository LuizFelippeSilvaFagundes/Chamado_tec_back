from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List, Optional
from app.models import User, RoleEnum
from schemas import UserCreate, UserUpdate
from app.services.auth_service import AuthService

class UserService:
    @staticmethod
    def create_user(db: Session, user: UserCreate) -> User:
        """Cria um novo usuário"""
        hashed_password = AuthService.get_password_hash(user.password)
        db_user = User(
            username=user.username,
            email=user.email,
            full_name=user.full_name,
            hashed_password=hashed_password,
            role=user.role,
            is_active=True,
            is_approved=True if user.role == RoleEnum.user else False,  # Usuários normais são aprovados automaticamente
            # Campos específicos de técnico
            employee_id=user.employee_id,
            department=user.department,
            specialty=user.specialty,
            phone=user.phone,
            emergency_contact=user.emergency_contact,
            certifications=user.certifications,
            experience_years=user.experience_years,
            availability=user.availability,
            notes=user.notes
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user

    @staticmethod
    def get_user_by_username(db: Session, username: str) -> Optional[User]:
        """Busca usuário por username"""
        return db.query(User).filter(User.username == username).first()

    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        """Busca usuário por email"""
        return db.query(User).filter(User.email == email).first()

    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
        """Busca usuário por ID"""
        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    def get_users_by_role(db: Session, role: RoleEnum, skip: int = 0, limit: int = 100) -> List[User]:
        """Busca usuários por role"""
        return db.query(User).filter(User.role == role).offset(skip).limit(limit).all()

    @staticmethod
    def get_pending_technicians(db: Session) -> List[User]:
        """Busca técnicos pendentes de aprovação"""
        return db.query(User).filter(
            and_(User.role == RoleEnum.technician, User.is_approved == False)
        ).all()

    @staticmethod
    def approve_technician(db: Session, technician_id: int) -> Optional[User]:
        """Aprova um técnico"""
        technician = UserService.get_user_by_id(db, technician_id)
        if technician and technician.role == RoleEnum.technician:
            technician.is_approved = True
            db.commit()
            db.refresh(technician)
        return technician

    @staticmethod
    def update_user(db: Session, user_id: int, user_update: UserUpdate) -> Optional[User]:
        """Atualiza dados do usuário"""
        db_user = UserService.get_user_by_id(db, user_id)
        if db_user:
            update_data = user_update.dict(exclude_unset=True)
            for field, value in update_data.items():
                if hasattr(db_user, field) and value is not None:
                    setattr(db_user, field, value)
            db.commit()
            db.refresh(db_user)
        return db_user

    @staticmethod
    def check_user_exists(db: Session, username: str, email: str) -> tuple[bool, str]:
        """Verifica se usuário já existe e retorna erro específico"""
        if UserService.get_user_by_username(db, username):
            return True, "Usuário já existe"
        if UserService.get_user_by_email(db, email):
            return True, "Email já cadastrado"
        return False, ""

    @staticmethod
    def is_technician_or_admin(user: User) -> bool:
        """Verifica se usuário é técnico ou admin"""
        return user.role in [RoleEnum.technician, RoleEnum.admin]

    @staticmethod
    def is_admin(user: User) -> bool:
        """Verifica se usuário é admin"""
        return user.role == RoleEnum.admin