from typing import Any
from fastapi.responses import JSONResponse

def success_response(message: str, data: Any = None, status_code: int = 200) -> JSONResponse:
    response_data = {
        "status": "success",
        "message": message,
    }
    if data is not None:
        response_data["data"] = data

    return JSONResponse(status_code=status_code, content=response_data)


def error_response(
    message: str, status_code: int = 400, error: str = None
) -> JSONResponse:
    response_data = {
        "status": "error",
        "message": message,
    }
    if error is not None:
        response_data["error"] = error

    return JSONResponse(status_code=status_code, content=response_data)
