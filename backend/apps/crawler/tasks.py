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
        from apps.analyzers.eeat.scorer import process_eeat_scoring
        from apps.analyzers.seo_audit.keyword_analyzer import process_keyword_analysis
        from apps.analyzers.seo_audit.technical_audit import process_technical_audit
        
        process_llms_txt_job(job_id)
        process_sitemap_job(job_id)
        process_schema_validation(job_id)
        process_eeat_scoring(job_id)
        process_keyword_analysis(job_id)
        process_technical_audit(job_id)
        
    except Exception as e:
        logger.error(f"Crawl job {job_id} failed: {e}")
        try:
            job = CrawlJob.objects.get(id=job_id)
            job.status = 'failed'
            job.save()
        except CrawlJob.DoesNotExist:
            pass
