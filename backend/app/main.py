from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.api.router import api_router
from app.core.config import get_settings
from app.db.mysql import SessionLocal
from app.db.neo4j import get_neo4j_manager
from app.services.user_service import UserService

settings = get_settings()
neo4j_manager = get_neo4j_manager()


@asynccontextmanager
async def lifespan(_: FastAPI):
    session = SessionLocal()
    if not settings.demo_mode:
        neo4j_manager.connect()
    try:
        session.execute(text("SELECT 1"))
        UserService(session).ensure_admin_user(settings.admin_username, settings.admin_password)
    finally:
        session.close()
    try:
        yield
    finally:
        neo4j_manager.close()


app = FastAPI(title=settings.app_name, version=settings.app_version, lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(api_router, prefix=settings.api_prefix)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
