from .auth import router as auth_router
from .workspace import router as workspace_router
from .chat import router as chat_router
from .admin import router as admin_router
from .users import router as users_router
from .assign_ws import router as assign_ws_router

__all__ = [
    "auth_router",
    "workspace_router",
    "chat_router",
    "admin_router",
    "users_router",
    "assign_ws_router"
]
