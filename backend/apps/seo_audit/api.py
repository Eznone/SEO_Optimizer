from ninja import Router
from .schemas import AuditRequest, AuditResponse, Error
from apps.crawler.models import CrawlJob
from apps.crawler.tasks import run_crawl_job

router = Router()

@router.post("/audit", response={200: AuditResponse, 400: Error, 500: Error})
def start_audit(request, data: AuditRequest):
    """
    DEPRECATED: Use /api/crawler/start instead.
    This legacy endpoint now maps to the new Crawler architecture.
    """
    try:
        # Map legacy request to new CrawlJob
        job = CrawlJob.objects.create(
            target_url=data.url,
            target_keywords=data.target_keywords
        )
        run_crawl_job.delay(str(job.id))
        
        return {
            "message": "SEO audit started (Migrated to Crawler)",
            "job_id": str(job.id)
        }
    except Exception as e:
        return 500, {
            "error": str(e),
            "message": "Failed to start migrated audit task"
        }

@router.get("/audit/{job_id}")
def get_audit_result(request, job_id: str):
    """
    DEPRECATED: Use /api/crawler/status/{job_id} instead.
    """
    from django.shortcuts import redirect
    # We can't easily redirect a ninja response to another router's URL path without hardcoding
    # So we just return the status from the new model
    try:
        job = CrawlJob.objects.get(id=job_id)
        return {
            "status": job.status,
            "message": "This endpoint is deprecated. Please use /api/crawler/status/{id} for detailed results.",
            "job_id": str(job.id)
        }
    except CrawlJob.DoesNotExist:
        return 404, {"message": "Job not found"}
