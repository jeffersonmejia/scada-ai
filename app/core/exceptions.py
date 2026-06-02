class AppError(Exception):
    status_code = 500

    def __init__(self, message: str, service: str | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.service = service


class UnauthorizedError(AppError):
    status_code = 401


class ServiceUnavailableError(AppError):
    status_code = 503


class ValidationBlockedError(AppError):
    status_code = 400

