from ninja import Router
from django.shortcuts import get_object_or_404
from typing import List
from .models import CrawlJob, AuditIssue, Recommendation, CrawledPage
from .schemas import CrawlJobCreate, CrawlJobResponse, AuditIssueSchema, RecommendationSchema, CrawledPageSchema
from .tasks import run_crawl_job

router = Router()

@router.post("/start", response={200: dict})
def create_crawl_job(request, data: CrawlJobCreate):
    job = CrawlJob.objects.create(
        user=request.auth,
        target_url=str(data.target_url),
        target_keywords=data.target_keywords or []
    )
    run_crawl_job.delay(str(job.id))
    return {"job_id": str(job.id), "message": "Crawl job started"}

@router.get("/status/{job_id}", response=CrawlJobResponse)
def get_crawl_job(request, job_id: str):
    job = get_object_or_404(CrawlJob, id=job_id, user=request.auth)
    return job

@router.get("/status/{job_id}/issues", response=List[AuditIssueSchema])
def get_job_issues(request, job_id: str):
    job = get_object_or_404(CrawlJob, id=job_id, user=request.auth)
    return list(AuditIssue.objects.filter(job=job).select_related('page'))

@router.get("/status/{job_id}/recommendations", response=List[RecommendationSchema])
def get_job_recommendations(request, job_id: str):
    job = get_object_or_404(CrawlJob, id=job_id, user=request.auth)
    return list(Recommendation.objects.filter(job=job).order_by('priority'))

@router.get("/status/{job_id}/pages", response=List[CrawledPageSchema])
def get_job_pages(request, job_id: str):
    job = get_object_or_404(CrawlJob, id=job_id, user=request.auth)
    return list(CrawledPage.objects.filter(job=job))

@router.get("/jobs", response=List[CrawlJobResponse])
def list_crawl_jobs(request):
    return list(CrawlJob.objects.filter(user=request.auth).order_by('-created_at'))
