"""FastAPI application with user management endpoints."""
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.database import init_db
from app.routers import users, calculations

# Create FastAPI application
app = FastAPI(
    title="Secure User Management API",
    description="A secure FastAPI application with user registration and authentication",
    version="1.0.0"
)

app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.include_router(users.router)
app.include_router(calculations.router)

@app.on_event("startup")
def on_startup():
    """Initialize database on application startup."""
    init_db()

@app.get("/", tags=["Root"])
def read_root():
    """Root endpoint returning API information."""
    return {
        "message": "Welcome to Secure User Management API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health", tags=["Health"])
def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}

