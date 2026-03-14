from ninja import Router
from typing import List
from django.shortcuts import get_object_or_404
from .schemas import (
    SitemapCreateSchema, 
    SitemapResponseSchema, 
    RecommendationSchema, 
    IssueSchema, 
    PageSchema
)
from .models import SitemapJob, Recommendation, AuditIssue, Page
from .tasks import crawl_and_generate_sitemap

router = Router()

@router.post("/generate")
def create_sitemap_job(request, data: SitemapCreateSchema):
    """
    Submits a new sitemap job given a target URL.
    """
    job = SitemapJob.objects.create(target_url=data.target_url)

    # Starting Celery background task
    crawl_and_generate_sitemap.delay(str(job.id))
    return {
        "message": "Sitemap generation started",
        "job_id": str(job.id)
    }

@router.get("/generate/{job_id}", response=SitemapResponseSchema)
def get_sitemap_status(request, job_id: str):
    """
    Check the status of a specific sitemap generation job.
    """
    job = get_object_or_404(SitemapJob, id=job_id)
    if job.sitemap_file:
        job.sitemap_url = job.sitemap_file.url
    return job

@router.get("/generate/{job_id}/recommendations", response=List[RecommendationSchema])
def get_job_recommendations(request, job_id: str):
    """
    Get prioritized SEO recommendations based on the crawl.
    """
    job = get_object_or_404(SitemapJob, id=job_id)
    return list(Recommendation.objects.filter(job=job).order_by('priority'))

@router.get("/generate/{job_id}/issues", response=List[IssueSchema])
def get_job_issues(request, job_id: str):
    """
    Get detailed SEO issues found during the crawl.
    """
    job = get_object_or_404(SitemapJob, id=job_id)
    return list(AuditIssue.objects.filter(job=job).select_related('page'))

@router.get("/generate/{job_id}/pages", response=List[PageSchema])
def get_job_pages(request, job_id: str):
    """
    Get a list of all pages crawled for the given job.
    """
    job = get_object_or_404(SitemapJob, id=job_id)
    return list(Page.objects.filter(job=job))
