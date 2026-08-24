from fastapi import Request
from fastapi.responses import JSONResponse


# Custom errors used across the backend
class AppError(Exception):

    def __init__(
        self,
        error: str,
        code: str,
        detail: str,
        status_code: int = 400,
    ):
        self.error = error
        self.code = code
        self.detail = detail
        self.status_code = status_code


class JobNotFound(AppError):

    def __init__(self, job_id: str):
        super().__init__(
            error="Research job not found",
            code="JOB_NOT_FOUND",
            detail=f"No research job exists for id {job_id}",
            status_code=404,
        )


class ValidationFailed(AppError):

    def __init__(self, detail: str):
        super().__init__(
            error="Validation failed",
            code="VALIDATION_FAILED",
            detail=detail,
            status_code=422,
        )


async def app_error_handler(
    request: Request,
    exc: AppError,
):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.error,
            "code": exc.code,
            "detail": exc.detail,
        },
    )