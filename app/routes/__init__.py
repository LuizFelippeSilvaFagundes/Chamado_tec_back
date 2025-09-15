from .auth_routes import router as auth_router
from .user_routes import router as user_router
from .ticket_routes import router as ticket_router
from .tech_routes import router as tech_router
from .admin_routes import router as admin_router

__all__ = [
    "auth_router",
    "user_router", 
    "ticket_router",
    "tech_router",
    "admin_router"
]