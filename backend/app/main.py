import logging
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.config import get_settings
from app.api.v1 import api_router

logger = logging.getLogger(__name__)
settings = get_settings()
app = FastAPI(title="Data Quality Platform API", version="1.0.0")


@app.exception_handler(Exception)
def global_exception_handler(_request: Request, exc: Exception):
    """Ensure unhandled 500 errors return JSON with detail."""
    if isinstance(exc, HTTPException):
        raise exc  # Let FastAPI handle HTTPException
    logger.exception("Unhandled exception: %s", exc)
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc)},
    )

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")


@app.get("/")
def root():
    return {"message": "Data Quality Platform API", "docs": "/docs"}
