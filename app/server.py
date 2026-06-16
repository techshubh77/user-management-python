# app/server.py
import sys
import asyncio
import uvicorn
from sqlalchemy import text

from app.main import app  # Import your configured application layer
from app.config.settings import settings
from app.utils.logger import logger
from app.config.database import engine  # Your SQLAlchemy engine object

is_shutting_down = False


async def shutdown_connections():
    """Isolated dependency cleanup runner (Triggers automatically on shutdown)."""
    global is_shutting_down
    if is_shutting_down:
        return
    is_shutting_down = True

    try:
        logger.info("🛑 Commencing shutdown logic...")
        logger.info("Closing active system connection pipelines...")

        if engine:
            await engine.dispose()  # Close SQLAlchemy database pools cleanly

        logger.info("✨ Shutdown procedure complete.")
    except Exception as err:
        logger.error(f"FORCED SYSTEM SHUTDOWN FAILURE: {err}")
        sys.exit(1)


# Register the hook directly onto the FastAPI app instance for clean shutdown
app.on_event("shutdown")(shutdown_connections)


async def check_database_connection():
    """Verify pool driver stability before spinning up port interfaces."""
    try:
        logger.info("Authenticating underlying relational database configurations...")
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        logger.info("✅ Database connectivity verified successfully.")
    except Exception as e:
        logger.critical(f"💥 Database connection handshake failed: {e}")
        raise e


def start_server():
    """Server Start Logic (Equivalent to your Node startServer function)"""
    try:
        # 1. Run our pre-flight connection checks
        asyncio.run(check_database_connection())

        logger.info(f"🚀 Application initialized: {settings.app_name}")
        logger.info(f"Environment Profile: {settings.env}")
        logger.info(
            f"Binding network listeners onto local loopback port: {settings.port}"
        )

        # 2. 💡 Fixed: Use uvicorn.run directly so the hot-reload subprocess engine works!
        uvicorn.run(
            "app.main:app",  # Point directly to the app layout file path
            host="127.0.0.1",
            port=settings.port,
            reload=(settings.env == "development"),  # Toggle hot-reloading cleanly
            reload_dirs=(
                ["app"] if settings.env == "development" else None
            ),  # Watch the app folder
            log_level="info",
        )

    except Exception as error:
        logger.critical(
            f"CRITICAL SYSTEM EXECUTION ENGINES COMPROMISED! Failed to start server: {error}"
        )
        sys.exit(1)


if __name__ == "__main__":
    start_server()
