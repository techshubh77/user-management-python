from contextlib import asynccontextmanager
import sys
from starlette.exceptions import HTTPException as StarletteHTTPException

import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from sqlalchemy import text
from fastapi.routing import APIRouter

import secure
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app.config.database import engine
from app.routes.index import app_routes
from app.config.settings import settings
from fastapi.exceptions import RequestValidationError
from app.exceptions.handlers import (
    app_exception_handler,
    validation_exception_handler,
    global_exception_handler,
    http_exception_handler
)
from app.exceptions.custom_exceptions import AppException
from app.utils.logger import logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        logger.info("Authenticating underlying relational database configurations...")
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        logger.info("Database connectivity verified successfully.")
    except Exception as e:
        logger.critical(f"Database connection handshake failed: {e}")
        raise e

    logger.info(f"Application initialized: {settings.app_name}")
    logger.info(f"Environment Profile: {settings.env}")
    logger.info(f"Binding network listeners onto port: {settings.port}")

    yield  # app runs here

    logger.info("Commencing shutdown logic...")
    try:
        if engine:
            await engine.dispose()
        logger.info("Shutdown procedure complete.")
    except Exception as err:
        logger.error(f"FORCED SYSTEM SHUTDOWN FAILURE: {err}")
        sys.exit(1)


app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    docs_url="/docs" if settings.env == "development" else None,
    lifespan=lifespan,
)

# API Version Router
api_v1_router = APIRouter(prefix="/api/v1")
api_v1_router.include_router(app_routes)
app.include_router(api_v1_router)

# middleware definitions
# goes from top to bottom : execution goes CORS -> GZip -> SlowAPI -> Secure Headers -> Routes

# Secure Headers
secure_headers = secure.Secure()
@app.middleware("http")
async def set_secure_headers(request: Request, call_next):
    response = await call_next(request)
    secure_headers.set_headers(response)
    return response

# GZip Compression
app.add_middleware(GZipMiddleware, minimum_size=1000)

# SlowAPI Rate Limiting
limiter = Limiter(key_func=get_remote_address, default_limits=["100/15 minutes"])
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# CORS
allowed_origins = settings.allowed_origins.split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=["Content-Type", "Authorization"],
)


# --- CUSTOM EXCEPTION HANDLERS ---
app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, global_exception_handler)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)


def start_server():
    """Start the FastAPI server directly via Uvicorn execution entry point."""
    try:
        uvicorn.run(
            "app.main:app",
            host="127.0.0.1",
            port=settings.port,
            reload=(settings.env == "development"),
            reload_dirs=["app"] if settings.env == "development" else None,
            log_level="info",
        )
    except Exception as error:
        logger.critical(
            f"CRITICAL SYSTEM EXECUTION ENGINES COMPROMISED! Failed to start server: {error}"
        )
        sys.exit(1)


if __name__ == "__main__":
    start_server()
