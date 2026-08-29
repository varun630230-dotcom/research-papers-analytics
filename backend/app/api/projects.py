from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import get_db
from app.models.models import Project
from app.schemas.requests import AnalyzeRequest, ExportRequest
from app.schemas.responses import AnalyzeResponse, StatusResponse, ExportResponse, ProjectResult, AnalysisProgress
from app.services.pipeline import AnalysisPipeline
from app.services.report_generation import ReportGenerationService
from app.config import settings
import json

router = APIRouter(prefix="/api/projects", tags=["projects"])

@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_project(request: AnalyzeRequest, background_tasks: BackgroundTasks, db: AsyncSession = Depends(get_db)):
    new_project = Project(
        idea=request.idea,
        goal=request.goal,
        domain=request.domain,
        technical_level=request.technical_level,
        constraints=request.constraints,
        status="analyzing"
    )
    db.add(new_project)
    await db.commit()
    await db.refresh(new_project)

    pipeline = AnalysisPipeline(settings)
    background_tasks.add_task(pipeline.run, new_project.id, request, db)

    return AnalyzeResponse(project_id=new_project.id)

@router.get("/{project_id}", response_model=ProjectResult)
async def get_project(project_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Project).filter(Project.id == project_id))
    project = result.scalars().first()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    prog_data = json.loads(project.progress_data) if project.progress_data else {"current_stage": 0, "total_stages": 11, "stages": []}
    res_data = json.loads(project.results_data) if project.results_data else {}
    
    return ProjectResult(
        id=project.id,
        idea=project.idea,
        goal=project.goal or "",
        domain=project.domain or "",
        technical_level=project.technical_level or "",
        constraints=project.constraints or "",
        status=project.status,
        progress=AnalysisProgress(**prog_data),
        created_at=project.created_at.isoformat(),
        completed_at=project.completed_at.isoformat() if project.completed_at else None,
        error_message=project.error_message,
        **res_data
    )

@router.get("/{project_id}/status", response_model=StatusResponse)
async def get_status(project_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Project).filter(Project.id == project_id))
    project = result.scalars().first()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
        
    prog_data = json.loads(project.progress_data) if project.progress_data else {"current_stage": 0, "total_stages": 11, "stages": []}
    return StatusResponse(status=project.status, progress=AnalysisProgress(**prog_data))

@router.post("/{project_id}/export", response_model=ExportResponse)
async def export_project(project_id: str, request: ExportRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Project).filter(Project.id == project_id))
    project = result.scalars().first()
    
    if not project or project.status != "completed":
        raise HTTPException(status_code=400, detail="Project not completed or not found")
        
    res_data = json.loads(project.results_data) if project.results_data else {}
    prog_data = json.loads(project.progress_data) if project.progress_data else {"current_stage": 0, "total_stages": 11, "stages": []}
    
    proj_res = ProjectResult(
        id=project.id,
        idea=project.idea,
        goal=project.goal or "",
        domain=project.domain or "",
        technical_level=project.technical_level or "",
        constraints=project.constraints or "",
        status=project.status,
        progress=AnalysisProgress(**prog_data),
        created_at=project.created_at.isoformat(),
        **res_data
    )
    
    rg_svc = ReportGenerationService()
    if request.format == "markdown":
        content = rg_svc.generate_markdown(proj_res)
        filename = f"report_{project_id}.md"
    else:
        content = rg_svc.generate_json(proj_res)
        filename = f"report_{project_id}.json"
        
    return ExportResponse(content=content, filename=filename)
