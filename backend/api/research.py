# FastAPI and project imports used for the research routes

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from backend.core.auth import get_current_user
from backend.services.research_service import ResearchService


# 
from backend.repositories.research_job_repository import (ResearchJobRepository)
from backend.repositories.planner_task_repository import (PlannerTaskRepository)
from backend.repositories.source_repository import (SourceRepository)
from backend.repositories.evidence_repository import (EvidenceRepository)
from backend.repositories.validation_repository import (ValidationRepository)
from backend.repositories.report_repository import (ReportRepository)



# Router
router = APIRouter(
    prefix="/api/research",
    tags=["Research"],
)




class ResearchRequest(BaseModel):
    query: str


class ResearchResponse(BaseModel):
    job_id: str
    status: str
    title: str
    executive_summary: str


def _ensure_owner(job: dict, user) -> None:
    """Ensures the authenticated user owns this job (when ownership is set)."""

    owner = job.get("created_by")

    if owner and owner != user.id:
        raise HTTPException(
            status_code=403,
            detail="You do not have access to this research job.",
        )





research_job_repository = ResearchJobRepository()

planner_task_repository = PlannerTaskRepository()

source_repository = SourceRepository()

evidence_repository = EvidenceRepository()

validation_repository = ValidationRepository()

report_repository = ReportRepository()

research_service = ResearchService()





@router.get("/")
def list_research_jobs(
    user=Depends(get_current_user),
):
    jobs = research_job_repository.list_jobs(created_by=user.id)

    return {
        "count": len(jobs),
        "jobs": jobs,
    }


@router.post(
    "/",
    response_model=ResearchResponse,
)
def create_research(
    request: ResearchRequest,
    user=Depends(get_current_user),
):

    # Validating query

    if not request.query or not request.query.strip():

        raise HTTPException(
            status_code=400,
            detail="Research query cannot be empty.",
        )

    # Creating research job

    try:

        job = research_job_repository.create_job(
            request.query.strip(),
            created_by=user.id,
        )

        job_id = job["id"]

        # Mark job as researching

        research_job_repository.update_status(job_id, "researching",)

        print(f"Research job created: {job_id}")

        # Runing AI pipeline

        result = research_service.run_research(query=request.query.strip(),job_id=job_id,)

        # Marking job completed

        research_job_repository.update_status(job_id,"completed",)

        print(f"Research job completed: {job_id}")

        # Return result

        return ResearchResponse(
            job_id=job_id,
            status="completed",
            title=result.report.title,
            executive_summary=(
                result.report.executive_summary
            ),
        )

    except ValueError as e:

        # Invalid research input pipeline validation error
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )

    except Exception as e:

       
        # Mark job as fail
        try:

            if "job_id" in locals():

                research_job_repository.update_status(
                    job_id,
                    "failed",
                )

        except Exception:
            pass

        print(f"Research pipeline failed: {e}")

        raise HTTPException(
            status_code=500,
            detail="Research pipeline failed.",
        )





# GET - Research Jov

@router.get("/{job_id}")
def get_research_job(
    job_id: str,
    user=Depends(get_current_user),
):

    job = research_job_repository.get_job(job_id)

    if not job:

        raise HTTPException(
            status_code=404,
            detail="Research job not found.",
        )

    _ensure_owner(job, user)

    return job




# GET - Research Taskd

@router.get("/{job_id}/tasks")
def get_research_tasks(
    job_id: str,
    user=Depends(get_current_user),
):

    job = research_job_repository.get_job(job_id)

    if not job:

        raise HTTPException(
            status_code=404,
            detail="Research job not found.",
        )

    _ensure_owner(job, user)

    tasks = planner_task_repository.get_tasks(
        job_id
    )

    return {
        "job_id": job_id,
        "count": len(tasks),
        "tasks": tasks,
    }




# GET - Research Sources

@router.get("/{job_id}/sources")

def get_research_sources(
    job_id: str,
    user=Depends(get_current_user),
):

    job = research_job_repository.get_job(job_id)

    if not job:

        raise HTTPException(
            status_code=404,
            detail="Research job not found.",
        )

    _ensure_owner(job, user)

    sources = source_repository.get_sources(
        job_id
    )

    return {
        "job_id": job_id,
        "count": len(sources),
        "sources": sources,
    }




# GET - research Evidence

@router.get("/{job_id}/evidence")
def get_research_evidence(
    job_id: str,
    user=Depends(get_current_user),
):

    job = research_job_repository.get_job(job_id)

    if not job:

        raise HTTPException(
            status_code=404,
            detail="Research job not found.",
        )

    _ensure_owner(job, user)

    evidence = evidence_repository.get_evidence(
        job_id
    )

    return {
        "job_id": job_id,
        "count": len(evidence),
        "evidence": evidence,
    }




# GET - Research Validations

@router.get("/{job_id}/validations")
def get_research_validations(
    job_id: str,
    user=Depends(get_current_user),
):

    job = research_job_repository.get_job(job_id)

    if not job:

        raise HTTPException(
            status_code=404,
            detail="Research job not found.",
        )

    _ensure_owner(job, user)

    evidence = evidence_repository.get_evidence(job_id)

    validations = []

    for item in evidence:

        item_validations = (
            validation_repository.get_validations(
                item["id"]
            )
        )

        validations.extend(
            item_validations
        )

    return {
        "job_id": job_id,
        "count": len(validations),
        "validations": validations,
    }




# GET - Final Research Report

@router.get("/{job_id}/report")
def get_research_report(
    job_id: str,
    user=Depends(get_current_user),
):

    job = research_job_repository.get_job(job_id)

    if not job:

        raise HTTPException(
            status_code=404,
            detail="Research job not found.",
        )

    _ensure_owner(job, user)
    # _ensure_owner(job)

    reports = report_repository.get_reports(
        job_id
    )

    if not reports:

        raise HTTPException(
            status_code=404,
            detail="Research report not found.",
        )

    return {
        "job_id": job_id,
        "report": reports[0],
    }