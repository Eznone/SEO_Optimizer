from ninja import Router
from django.shortcuts import get_object_or_404
from typing import List
from .models import CrawlJob, AuditIssue, Recommendation
from .schemas import CrawlJobCreate, CrawlJobResponse, AuditIssueSchema, RecommendationSchema
from .tasks import run_crawl_job

router = Router()

@router.post("/start", response={200: dict})
def create_crawl_job(request, data: CrawlJobCreate):
    job = CrawlJob.objects.create(target_url=str(data.target_url))
    run_crawl_job.delay(str(job.id))
    return {"job_id": str(job.id), "message": "Crawl job started"}

@router.get("/status/{job_id}", response=CrawlJobResponse)
def get_crawl_job(request, job_id: str):
    job = get_object_or_404(CrawlJob, id=job_id)
    if job.generated_llms_txt:
        job.llms_txt_url = job.generated_llms_txt.url
    if job.generated_sitemap:
        job.sitemap_url = job.generated_sitemap.url
    return job

@router.get("/status/{job_id}/issues", response=List[AuditIssueSchema])
def get_job_issues(request, job_id: str):
    job = get_object_or_404(CrawlJob, id=job_id)
    return list(AuditIssue.objects.filter(job=job).select_related('page'))

@router.get("/status/{job_id}/recommendations", response=List[RecommendationSchema])
def get_job_recommendations(request, job_id: str):
    job = get_object_or_404(CrawlJob, id=job_id)
    return list(Recommendation.objects.filter(job=job).order_by('priority'))
