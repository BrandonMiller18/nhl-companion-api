"""FastAPI application for NHL Companion public API."""
import logging

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from api.router import router
from nhl_db.logging_config import setup_logging

# Initialize logging
setup_logging()
logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title="NHL Companion API",
    description="Public API for accessing NHL game, team, and player data",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS - adjust origins as needed for production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["*"],
)


# Custom exception handlers for clean JSON error responses
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Handle validation errors with clean JSON response."""
    logger.warning(f"Validation error on {request.url}: {exc.errors()}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": "Invalid request parameters",
            "errors": exc.errors()
        },
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle unexpected errors with clean JSON response."""
    logger.error(f"Unexpected error on {request.url}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "An unexpected error occurred"
        },
    )


# Health check endpoint (no authentication required)
@app.get("/health", tags=["health"])
async def health_check() -> dict:
    """
    Health check endpoint.
    
    Returns the API status without requiring authentication.
    """
    return {
        "status": "healthy",
        "service": "NHL Companion API",
        "version": "1.0.0"
    }


# Include the main API router
app.include_router(router)


# Startup event
@app.on_event("startup")
async def startup_event() -> None:
    """Log application startup."""
    logger.info("NHL Companion API starting up")


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event() -> None:
    """Log application shutdown."""
    logger.info("NHL Companion API shutting down")


if __name__ == "__main__":
    import uvicorn
    
    # Get configuration from environment or use defaults
    import os
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", "8000"))
    
    logger.info(f"Starting NHL Companion API on {host}:{port}")
    uvicorn.run(
        "api_app:app",
        host=host,
        port=port,
        reload=True,
        log_level="info"
    )

