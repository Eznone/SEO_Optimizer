from celery import shared_task
from .models import SitemapJob
from .services import SitemapGenerator
from django.core.files.base import ContentFile
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import logging

logger = logging.getLogger(__name__)

@shared_task
def crawl_and_generate_sitemap(job_id):
    job = SitemapJob.objects.get(id=job_id)
    job.status = 'processing'
    job.save()

    try:
        logger.info(f"Starting crawl for: {job.target_url}")

        # Use requests for better compatibility with eventlet on Windows
        response = requests.get(job.target_url, timeout=10.0, allow_redirects=True)
        response.raise_for_status()
        html_content = response.text

        logger.info(f"Successfully fetched HTML. Content length: {len(html_content)}")

        soup = BeautifulSoup(html_content, 'html.parser')
        base_url = job.target_url
        domain = urlparse(base_url).netloc

        logger.info(f"Parsing links for domain: {domain}")

        # Robust URL extraction: handles relative paths and filters for same domain
        links = set()
        for a in soup.find_all('a', href=True):
            href = a.get('href')
            full_url = urljoin(base_url, href)

            # Basic validation: ensure it's the same domain and starts with http/https
            parsed_url = urlparse(full_url)
            if parsed_url.netloc == domain and parsed_url.scheme in ('http', 'https'):
                # Normalize URL by removing fragments
                normalized_url = parsed_url._replace(fragment='').geturl()
                links.add(normalized_url)

        logger.info(f"Found {len(links)} internal links. Generating XML...")

        # Generate XML
        generator = SitemapGenerator(list(links))
        xml_content = generator.generate_xml()

        logger.info("XML generated. Saving to file...")

        def perform_save():
            import os
            from eventlet.patcher import original
            
            # Get the original, unpatched os module
            orig_os = original('os')
            
            # Store the patched fdopen
            patched_fdopen = os.fdopen
            
            # Temporarily restore the original fdopen
            os.fdopen = orig_os.fdopen
            try:
                job.sitemap_file.save(f"{job.id}.xml", ContentFile(xml_content))
            finally:
                # Always restore the patched version for Eventlet's sake
                os.fdopen = patched_fdopen

        # Execute the save in a thread pool
        try:
            from eventlet import tpool
            tpool.execute(perform_save)
        except (ImportError, AttributeError):
            # Fallback for non-eventlet environments
            job.sitemap_file.save(f"{job.id}.xml", ContentFile(xml_content))

        logger.info("File saved successfully.")

        job.status = 'completed'
    except Exception as e:
        logger.error(f"Error generating sitemap for job {job_id}: {str(e)}", exc_info=True)
        job.status = 'failed'

    job.save()