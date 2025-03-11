import os
from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.agents.api.routes import router as agents_router
from app.ms_auth.api.routes import router as ms_auth_router
from app.chat.api.routes import router as chat_router
from app.file_upload.api.routes import router as file_upload_router
from sync_blob import startup_event

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Code to run on startup
    await startup_event()
    yield
    # Code to run on shutdown

app = FastAPI(lifespan=lifespan)
app.include_router(agents_router, prefix="/api", tags=["agents"])
app.include_router(ms_auth_router, prefix="/api", tags=["ms_auth"])
app.include_router(chat_router, prefix="/api", tags=["chat"])
app.include_router(file_upload_router, prefix="/api", tags=["file_upload"])