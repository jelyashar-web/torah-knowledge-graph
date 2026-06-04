"""Ingestion job management API."""

import uuid
from datetime import datetime
from typing import Any

import structlog
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.db import get_db
from app.models import IngestionJob, JobStatus
from app.tasks import extract_from_sefaria

logger = structlog.get_logger()
router = APIRouter(prefix="/api/v1/ingest", tags=["ingestion"])


class CreateJobRequest(BaseModel):
    book_title: str
    source_type: str = "sefaria"


class JobResponse(BaseModel):
    id: uuid.UUID
    book_title: str
    source_type: str
    status: str
    total_refs: int | None
    fetched_refs: int | None
    failed_refs: int | None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class BatchRequest(BaseModel):
    books: list[str]
    source_type: str = "sefaria"


@router.post("/jobs", status_code=status.HTTP_202_ACCEPTED)
async def create_job(
    req: CreateJobRequest,
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    job = IngestionJob(
        book_title=req.book_title,
        source_type=req.source_type,
        status=JobStatus.PENDING,
    )
    db.add(job)
    await db.commit()
    await db.refresh(job)

    if req.source_type == "sefaria":
        extract_from_sefaria.delay(str(job.id), req.book_title)
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"source_type '{req.source_type}' not yet supported",
        )

    logger.info("ingest_job_created", job=str(job.id), book=req.book_title)
    return {
        "job_id": str(job.id),
        "status": job.status,
        "book": job.book_title,
        "location": f"/api/v1/ingest/jobs/{job.id}",
    }


@router.get("/jobs/{job_id}", response_model=JobResponse)
async def get_job(job_id: str, db: AsyncSession = Depends(get_db)):
    from uuid import UUID
    try:
        uuid_obj = UUID(job_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid job_id")

    result = await db.execute(select(IngestionJob).where(IngestionJob.id == uuid_obj))
    job = result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
    return job


@router.get("/jobs")
async def list_jobs(
    status: str | None = None,
    limit: int = 20,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
):
    query = select(IngestionJob).order_by(IngestionJob.created_at.desc())
    if status:
        try:
            st = JobStatus(status)
            query = query.where(IngestionJob.status == st)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid status filter"
            )

    result = await db.execute(query.limit(limit).offset(offset))
    jobs = result.scalars().all()
    return {"items": jobs, "limit": limit, "offset": offset}


@router.post("/batch", status_code=status.HTTP_202_ACCEPTED)
async def create_batch(
    req: BatchRequest,
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    created = []
    for book in req.books:
        job = IngestionJob(
            book_title=book,
            source_type=req.source_type,
            status=JobStatus.PENDING,
        )
        db.add(job)
        await db.flush()
        if req.source_type == "sefaria":
            extract_from_sefaria.delay(str(job.id), book)
        created.append({"job_id": str(job.id), "book": book})

    await db.commit()
    logger.info("ingest_batch_created", count=len(created))
    return {"created": created, "count": len(created)}
