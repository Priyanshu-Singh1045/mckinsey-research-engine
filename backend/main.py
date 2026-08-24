import logging


# 
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware


# importing 
from backend.core.config import get_settings
from backend.core.errors import AppError, app_error_handler
from backend.core.logging import configure_logging
from backend.middleware.request_id import RequestIDMiddleware

# importing router
from backend.api.research import router as research_router
from backend.api.reports import router as reports_router
from backend.api.evidence import router as evidence_router
from backend.api.feedback import router as feedback_router


settings = get_settings()


configure_logging()



logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    description="AI Market Research & Strategy Engine",
)


# Add middleware and API routes
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(RequestIDMiddleware)

app.add_exception_handler(AppError,app_error_handler,)



app.include_router(research_router)
app.include_router(reports_router)
app.include_router(evidence_router)
app.include_router(feedback_router)


@app.get("/")
async def root():
    return {
        "name": settings.app_name,
        "status": "running",
    }


@app.get("/health")
async def health(request: Request):
    request_id = getattr(request.state, "request_id", None)

    logger.info(
        "Health check",
        extra={"request_id": request_id},
    )

    return {
        "status": "healthy",
        "request_id": request_id,
    }