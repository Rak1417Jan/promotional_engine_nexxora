"""
FastAPI Application Entry Point
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import init_db
from app.api.v1 import operators, players, events, campaigns, auth, imports, exports, insights, segments
from app.middleware.tenant_middleware import TenantMiddleware

# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-Powered iGaming Promotional Marketing Engine",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Tenant Middleware (must be after CORS)
app.add_middleware(TenantMiddleware)

# Include routers
app.include_router(auth.router, prefix="/api/v1")
app.include_router(operators.router, prefix="/api/v1")
app.include_router(players.router, prefix="/api/v1")
app.include_router(events.router, prefix="/api/v1")
app.include_router(campaigns.router, prefix="/api/v1")
app.include_router(imports.router, prefix="/api/v1")
app.include_router(exports.router, prefix="/api/v1")
app.include_router(insights.router, prefix="/api/v1")
app.include_router(segments.router, prefix="/api/v1")


@app.on_event("startup")
async def startup_event():
    """Initialize on startup"""
    # Database tables should be created via scripts/init_database.py
    # We don't auto-create on startup to avoid issues
    print(f"{settings.APP_NAME} v{settings.APP_VERSION} started successfully")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": f"Welcome to {settings.APP_NAME}",
        "version": settings.APP_VERSION,
        "docs": "/api/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

