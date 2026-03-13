from ninja import Router
from typing import List
from .schemas import SitemapCreateSchema, SitemapResponseSchema
from .models import SitemapJob
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
    job = SitemapJob.objects.get(id=job_id)
    # We can inject the file URL if it's finished
    if job.sitemap_file:
        job.sitemap_url = job.sitemap_file.url
    return job