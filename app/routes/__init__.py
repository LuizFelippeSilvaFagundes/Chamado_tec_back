from .auth_routes import router as auth_router
from .user_routes import router as user_router
from .ticket_routes import router as ticket_router
from .tech_routes import router as tech_router
from .admin_routes import router as admin_router
from .avatar_routes import router as avatar_router
from .attachment_routes import router as attachment_router

__all__ = [
    "auth_router",
    "user_router", 
    "ticket_router",
    "tech_router",
    "admin_router",
    "avatar_router",
    "attachment_router"
]
