# fastapi middleware
from fastapi import FastAPI
from starlette.middleware.gzip import GZipMiddleware
from fastapi.middleware.cors import CORSMiddleware
# global setting
from app.core.config import settings
from app.utils.error_handler import setup_exception_handlers
# lifespan
from contextlib import asynccontextmanager
# router
from app.api.v1.router import api_router


# lifespan 등록
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    print("Starting up FastAPI application...")

    # - init db

    # - ping es

    # process running
    yield

    # Shutdown
    # - DB connection close
    print("Shutting down FastAPI application...")


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan
)

# error handler
setup_exception_handlers(app)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# GZipMiddleware
app.add_middleware(
    GZipMiddleware,
    minimum_size=1024,     # 1KB 이상만 압축 (작은 바디는 역효과)
    compresslevel=6
)


# Health check API
@app.get("/health")
async def root():
    """Root endpoint"""
    return {
        "message": f"Welcome to {settings.APP_NAME}",
        "version": settings.APP_VERSION,
    }


# Include API routes
app.include_router(api_router, prefix="/api/v1")
