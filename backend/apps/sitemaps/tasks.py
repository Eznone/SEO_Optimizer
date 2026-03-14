from celery import shared_task
from .models import SitemapJob, Page
from .services import SitemapGenerator, SiteCrawler, SiteAnalyzer
from django.core.files.base import ContentFile
import logging
from django.utils import timezone

logger = logging.getLogger(__name__)

@shared_task
def crawl_and_generate_sitemap(job_id):
    try:
        job = SitemapJob.objects.get(id=job_id)
    except SitemapJob.DoesNotExist:
        logger.error(f"SitemapJob {job_id} not found.")
        return

    job.status = 'processing'
    job.save()

    try:
        logger.info(f"Starting deep crawl for: {job.target_url}")
        
        # 1. Crawl the site
        crawler = SiteCrawler(job, max_pages=500)
        crawler.crawl()

        # 2. Analyze the collected data for SEO issues
        logger.info(f"Analyzing crawl data for job {job_id}")
        analyzer = SiteAnalyzer(job)
        analyzer.analyze()

        # 3. Generate the XML Sitemap
        # Only include valid, indexable pages returning 200 OK
        valid_pages = Page.objects.filter(job=job, status_code=200, is_noindex=False)
        generator = SitemapGenerator(list(valid_pages))
        xml_content = generator.generate_xml()

        logger.info("XML generated. Saving to file...")

        def perform_save():
            import os
            from eventlet.patcher import original
            
            orig_os = original('os')
            patched_fdopen = os.fdopen
            os.fdopen = orig_os.fdopen
            try:
                job.sitemap_file.save(f"{job.id}.xml", ContentFile(xml_content))
            finally:
                os.fdopen = patched_fdopen

        try:
            from eventlet import tpool
            tpool.execute(perform_save)
        except (ImportError, AttributeError):
            job.sitemap_file.save(f"{job.id}.xml", ContentFile(xml_content))

        logger.info("File saved successfully.")

        job.status = 'completed'
        job.completed_at = timezone.now()
    except Exception as e:
        logger.error(f"Error generating sitemap for job {job_id}: {str(e)}", exc_info=True)
        job.status = 'failed'
        job.completed_at = timezone.now()

    job.save()
