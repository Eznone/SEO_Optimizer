import logging
from celery import shared_task
from .models import CrawlJob
from .scraper import SiteCrawler

logger = logging.getLogger(__name__)

@shared_task
def run_crawl_job(job_id: str):
    logger.info(f"Starting crawl job {job_id}")
    try:
        job = CrawlJob.objects.get(id=job_id)
        job.status = 'processing'
        job.save()

        crawler = SiteCrawler(job, max_pages=100)
        crawler.crawl()
        
        logger.info(f"Completed crawl job {job_id}")
        
        # Trigger analyzers
        from apps.analyzers.llms_txt.generator import process_llms_txt_job
        from apps.analyzers.sitemap.generator import process_sitemap_job
        from apps.analyzers.schema.validator import process_schema_validation
        
        process_llms_txt_job(job_id)
        process_sitemap_job(job_id)
        process_schema_validation(job_id)
        
    except Exception as e:
        logger.error(f"Crawl job {job_id} failed: {e}")
        try:
            job = CrawlJob.objects.get(id=job_id)
            job.status = 'failed'
            job.save()
        except CrawlJob.DoesNotExist:
            pass
