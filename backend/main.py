from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import create_tables
from app.api.projects import router as projects_router
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_tables()
    yield

app = FastAPI(
    title="INNOVATE AI API",
    description="AI Research & Innovation Intelligence Platform",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(projects_router)

@app.get("/api/health")
async def health_check():
    return {"status": "ok", "llm_configured": settings.has_llm_provider}

@app.get("/")
async def root():
    return {"message": "Welcome to INNOVATE AI Backend"}
