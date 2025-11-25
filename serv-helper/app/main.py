from fastapi import FastAPI
from app.api import auth_router, workspace_router, chat_router, admin_router, users_router, assign_ws_router


app = FastAPI(
    title="Automation Service",
    description="Middleware service orchestrating AnythingLLM + frontend",
    version="1.0.0",
)

# Register routes
app.include_router(auth_router)
app.include_router(workspace_router)
app.include_router(chat_router)
app.include_router(admin_router)
app.include_router(users_router)
app.include_router(assign_ws_router)
