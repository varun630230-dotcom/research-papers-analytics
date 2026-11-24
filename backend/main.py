"""
ResearchGap AI - Main Application
====================================
Entry point for the FastAPI application.

This file does three things:
1. Creates the FastAPI application instance
2. Configures middleware (CORS, static files)
3. Registers all API route handlers
4. Initializes the database on startup

To run:
    cd backend
    uvicorn main:app --reload --port 8000

Then open:
    http://localhost:8000       → Frontend (dashboard)
    http://localhost:8000/docs  → Interactive API documentation
"""

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from datetime import datetime

# Import our modules
from config import config, validate_config
import database as db

# Import route handlers
from routes.research import router as research_router
from routes.papers import router as papers_router
from routes.export import router as export_router


# =============================================================================
# CREATE THE APPLICATION
# =============================================================================

app = FastAPI(
    title="ResearchGap AI",
    description=(
        "Intelligent Research Paper Analysis & Gap Detection Platform. "
        "Discovers academic papers, analyzes research gaps, identifies "
        "market opportunities, and generates evidence-based recommendations."
    ),
    version="1.0.0",
)


# =============================================================================
# MIDDLEWARE
# =============================================================================

# CORS (Cross-Origin Resource Sharing) allows the frontend to talk to the backend
# when they might be on different ports during development.
app.add_middleware(
    CORSMiddleware,
    allow_origins=config["CORS_ORIGINS"],
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)


# =============================================================================
# STATIC FILES (Frontend)
# =============================================================================

# Serve the frontend files (HTML, CSS, JS) from the /static path
frontend_path = os.path.join(os.path.dirname(__file__), "..", "frontend")
frontend_path = os.path.abspath(frontend_path)

if os.path.exists(frontend_path):
    app.mount("/static", StaticFiles(directory=frontend_path), name="static")


# =============================================================================
# REGISTER API ROUTES
# =============================================================================

app.include_router(research_router)
app.include_router(papers_router)
app.include_router(export_router)


# =============================================================================
# ROOT AND HEALTH ENDPOINTS
# =============================================================================

@app.get("/", include_in_schema=False)
async def serve_frontend():
    """
    Serves the main frontend page.
    When you visit http://localhost:8000/, you get the dashboard.
    """
    index_path = os.path.join(frontend_path, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {
        "message": "ResearchGap AI API is running. Frontend not found.",
        "docs": "/docs",
    }


@app.get("/health", tags=["System"])
async def health_check():
    """
    Health check endpoint.
    
    Used to verify the API is running and check configuration status.
    Returns the status of key components.
    """
    config_issues = validate_config()
    
    return {
        "status": "healthy",
        "version": "1.0.0",
        "database": "connected",
        "gemini_configured": len(config["GEMINI_API_KEY"]) > 0,
        "config_issues": config_issues,
        "timestamp": datetime.now().isoformat(),
    }


# =============================================================================
# STARTUP EVENT
# =============================================================================

@app.on_event("startup")
async def startup_event():
    """
    Runs when the application starts.
    
    - Validates configuration
    - Initializes the database (creates tables if needed)
    """
    print("=" * 60)
    print("  ResearchGap AI - Starting Up")
    print("=" * 60)
    
    # Check configuration
    issues = validate_config()
    if issues:
        print("\n⚠️  Configuration Issues:")
        for issue in issues:
            print(f"   - {issue}")
    else:
        print("✅ Configuration OK")
    
    # Initialize database
    db.initialize_database()
    print("✅ Database initialized")
    
    print(f"\n🌐 API Documentation: http://{config['HOST']}:{config['PORT']}/docs")
    print(f"🏠 Dashboard: http://{config['HOST']}:{config['PORT']}/")
    print("=" * 60)
