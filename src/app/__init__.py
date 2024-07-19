import os
from sanic import Sanic, Request
from sqlalchemy.ext.asyncio import create_async_engine
from contextvars import ContextVar
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from .routes import register_routes
from .models.models import User, Admin, BankAccounts, Transactions, Base
from dotenv import load_dotenv


if os.path.isfile(".env"):
    load_dotenv(".env")

app = Sanic(__name__)


POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "password")
POSTGRES_DB = os.getenv("POSTGRES_DB", "my_database")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")


bind = create_async_engine(f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}/{POSTGRES_DB}", echo=True)
_sessionmaker = sessionmaker(bind=bind, class_=AsyncSession, expire_on_commit=False)
_base_model_session_ctx = ContextVar("session")


@app.middleware("request")
async def inject_session(request: Request):
    request.ctx.session = _sessionmaker()
    request.ctx.session_ctx_token = _base_model_session_ctx.set(request.ctx.session)


@app.middleware("response")
async def close_session(request: Request, response):
    if hasattr(request.ctx, "session_ctx_token"):
        _base_model_session_ctx.reset(request.ctx.session_ctx_token)
        await request.ctx.session.close()


register_routes(app)

