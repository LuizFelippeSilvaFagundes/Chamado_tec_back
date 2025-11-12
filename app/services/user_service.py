from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.models import User
from app.schemas import UserCreate, UserUpdate
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
            is_approved=True if str(user.role) == "servidor" else False,  # Servidores são aprovados automaticamente
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
        import logging
        logger = logging.getLogger(__name__)
        
        try:
            logger.info(f"🔍 Executando query para buscar usuário: {username}")
            user = db.query(User).filter(User.username == username).first()
            logger.info(f"✅ Query executada com sucesso para: {username}")
            return user
        except Exception as e:
            logger.error(f"❌ Erro ao buscar usuário {username} no banco: {e}")
            import traceback
            logger.error(f"📍 Traceback: {traceback.format_exc()}")
            # Re-raise para que o erro seja tratado no nível superior
            raise

    @staticmethod
    def get_user_by_email(db: Session, email: Optional[str]) -> Optional[User]:
        """Busca usuário por email"""
        if not email:
            return None
        return db.query(User).filter(User.email == email).first()

    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
        """Busca usuário por ID"""
        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    def get_users_by_role(db: Session, role: str, skip: int = 0, limit: int = 100) -> List[User]:
        """Busca usuários por role"""
        return db.query(User).filter(User.role == role).offset(skip).limit(limit).all()

    @staticmethod
    def get_pending_technicians(db: Session) -> List[User]:
        """Busca técnicos pendentes de aprovação"""
        return db.query(User).filter(
            and_(User.role == "technician", User.is_approved == False)
        ).all()

    @staticmethod
    def approve_technician(db: Session, technician_id: int) -> Optional[User]:
        """Aprova um técnico"""
        technician = UserService.get_user_by_id(db, technician_id)
        if technician:
            role_str = str(technician.role.value) if hasattr(technician.role, 'value') else str(technician.role)
            if role_str == "technician":
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
                if value is not None:
                    setattr(db_user, field, value)
            db.commit()
            db.refresh(db_user)
        return db_user

    @staticmethod
    def update_user_password(db: Session, user_id: int, new_hashed_password: str) -> Optional[User]:
        """Atualiza a senha (hash) do usuário"""
        db_user = UserService.get_user_by_id(db, user_id)
        if db_user:
            db_user.hashed_password = new_hashed_password
            db.commit()
            db.refresh(db_user)
        return db_user

    @staticmethod
    def update_user_avatar(db: Session, user_id: int, avatar_url: str) -> Optional[User]:
        db_user = UserService.get_user_by_id(db, user_id)
        if db_user:
            db_user.avatar_url = avatar_url
            db.commit()
            db.refresh(db_user)
        return db_user

    @staticmethod
    def check_user_exists(db: Session, username: str, email: Optional[str]) -> Tuple[bool, str]:
        """Verifica se usuário já existe e retorna mensagem de erro"""
        existing_user = UserService.get_user_by_username(db, username)
        if existing_user:
            return True, "Username já está em uso"
        
        existing_email = UserService.get_user_by_email(db, email)
        if existing_email:
            return True, "Email já está em uso"
        
        return False, ""

    @staticmethod
    def deactivate_user(db: Session, user_id: int) -> Optional[User]:
        """Desativa um usuário"""
        db_user = UserService.get_user_by_id(db, user_id)
        if db_user:
            db_user.is_active = False
            db.commit()
            db.refresh(db_user)
        return db_user

    @staticmethod
    def activate_user(db: Session, user_id: int) -> Optional[User]:
        """Ativa um usuário"""
        db_user = UserService.get_user_by_id(db, user_id)
        if db_user:
            db_user.is_active = True
            db.commit()
            db.refresh(db_user)
        return db_user
