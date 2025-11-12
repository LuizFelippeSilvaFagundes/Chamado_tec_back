from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.dependencies import get_db
from app.controllers import AuthController
from app.schemas import ServidorRegister, AdminRegister
from app.models import User
from app.schemas import     UserCreate, UserLogin, TechRegister, UserResponse

router = APIRouter(tags=["Authentication"])

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user: ServidorRegister, db: Session = Depends(get_db)):
    """Registro de servidores (username, full_name, phone, password)"""
    return AuthController.register_servidor(db, user)

@router.post("/tech-register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_technician(tech: TechRegister, db: Session = Depends(get_db)):
    """Registro de técnicos"""
    return AuthController.register_technician(db, tech)

@router.post("/admin-register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_admin(admin: AdminRegister, db: Session = Depends(get_db)):
    """Registro de administradores"""
    return AuthController.register_admin(db, admin)

@router.post("/login", include_in_schema=True)
async def login(user: UserLogin, db: Session = Depends(get_db)):
    """Login de usuários com timeout"""
    import logging
    import asyncio
    from fastapi import HTTPException, status
    
    logger = logging.getLogger(__name__)
    
    try:
        logger.info(f"🔐 Tentativa de login para usuário: {user.username}")
        
        # Executar login com timeout de 10 segundos
        try:
            result = await asyncio.wait_for(
                asyncio.to_thread(AuthController.login, db, user),
                timeout=10.0
            )
            logger.info(f"✅ Login bem-sucedido para: {user.username}")
            return result
        except asyncio.TimeoutError:
            logger.error(f"⏱️ Timeout no login para {user.username} (10s)")
            raise HTTPException(
                status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                detail="Tempo de resposta excedido. Tente novamente."
            )
    except HTTPException:
        # Re-raise HTTPExceptions (incluindo timeout)
        raise
    except Exception as e:
        logger.error(f"❌ Erro no login para {user.username}: {e}")
        import traceback
        logger.error(f"📍 Traceback: {traceback.format_exc()}")
        # Retornar erro HTTP em vez de crashar
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno no servidor: {str(e)}"
        )

@router.get("/me")
def get_me(username: str = None, db: Session = Depends(get_db)):
    """Obter informações do usuário atual"""
    if username:
        from app.services.user_service import UserService
        user = UserService.get_user_by_username(db, username)
        if user:
            from app.schemas import UserResponse
            return UserResponse.from_orm(user)
        else:
            from fastapi import HTTPException
            raise HTTPException(status_code=404, detail="Usuário não encontrado")
    else:
        return {"message": "Username é obrigatório"}
