import traceback
from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from app.exceptions.custom_exceptions import AppException
from app.utils.logger import logger
from app.config.settings import settings


async def app_exception_handler(request: Request, exc: AppException):
    status = "fail" if 400 <= exc.status_code < 500 else "error"
    logger.warning(f"AppException [{exc.status_code}]: {exc.message}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": status,
            "message": exc.message,
        },
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = []
    for error in exc.errors():
        field = ".".join(str(loc) for loc in error["loc"][1:])
        msg = error["msg"]
        errors.append({"field": field, "message": msg})
    
    logger.warning(f"Validation Error: {errors}")
    return JSONResponse(
        status_code=422,
        content={
            "status": "fail",
            "message": "Validation failed",
            "errors": errors,
        },
    )


async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled Exception: {str(exc)}\n{traceback.format_exc()}")
    
    response_content = {
        "status": "error",
        "message": "Something went wrong!" if settings.env == "production" else str(exc),
    }
    
    if settings.env != "production":
        response_content["stack"] = traceback.format_exc()

    return JSONResponse(
        status_code=500,
        content=response_content,
    )
