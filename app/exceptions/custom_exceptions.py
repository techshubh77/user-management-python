class AppException(Exception):
    def __init__(self, message: str, status_code: int):
        self.message = message
        self.status_code = status_code


class BadRequestException(AppException):
    def __init__(
        self,
        message: str = "Bad Request",
    ):
        super().__init__(
            message=message,
            status_code=400,
        )


class UnauthorizedException(AppException):
    def __init__(
        self,
        message: str = "Unauthorized",
    ):
        super().__init__(
            message=message,
            status_code=401,
        )


class ForbiddenException(AppException):
    def __init__(
        self,
        message: str = "Forbidden",
    ):
        super().__init__(
            message=message,
            status_code=403,
        )


class NotFoundException(AppException):
    def __init__(
        self,
        message: str = "Resource Not Found",
    ):
        super().__init__(
            message=message,
            status_code=404,
        )


class ConflictException(AppException):
    def __init__(
        self,
        message: str = "Conflict",
    ):
        super().__init__(
            message=message,
            status_code=409,
        )
