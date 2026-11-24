"""
ResearchGap AI - Paper Routes
================================
API endpoints for retrieving paper details.
"""

from fastapi import APIRouter, HTTPException
import database as db

router = APIRouter(prefix="/papers", tags=["Papers"])


@router.get("/{project_id}")
async def get_project_papers(project_id: int, relevant_only: bool = False):
    """
    Returns all papers discovered for a research project.
    
    Query Parameters:
        relevant_only: If true, only return papers that passed filtering
    """
    project = db.get_project(project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Research project not found")
    
    papers = db.get_papers(project_id, relevant_only=relevant_only)
    
    return {
        "project_id": project_id,
        "topic": project["topic"],
        "papers": papers,
        "total": len(papers),
    }


@router.get("/{project_id}/analyses")
async def get_paper_analyses(project_id: int):
    """
    Returns the AI analysis results for each paper in a project.
    """
    project = db.get_project(project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Research project not found")
    
    analyses = db.get_paper_analyses(project_id)
    
    return {
        "project_id": project_id,
        "analyses": analyses,
        "total": len(analyses),
    }
