import xml.etree.ElementTree as ET
from datetime import datetime
from apps.crawler.models import CrawlJob, CrawledPage
from django.core.files.base import ContentFile
import logging

logger = logging.getLogger(__name__)

class SitemapGenerator:
    def __init__(self, job: CrawlJob, changefreq: str = "weekly"):
        self.job = job
        self.changefreq = changefreq
        self.generation_time = datetime.now().strftime('%Y-%m-%d')

    def generate_xml(self) -> bytes:
        pages = CrawledPage.objects.filter(job=self.job, status_code=200)
        urlset = ET.Element("urlset", xmlns="http://www.sitemaps.org/schemas/sitemap/0.9")

        for page in pages:
            url_el = ET.SubElement(urlset, "url")
            ET.SubElement(url_el, "loc").text = page.url
            ET.SubElement(url_el, "lastmod").text = self.generation_time
            ET.SubElement(url_el, "changefreq").text = self.changefreq
            ET.SubElement(url_el, "priority").text = str(page.priority)

        return ET.tostring(urlset, encoding='utf-8', method='xml', xml_declaration=True)

def process_sitemap_job(job_id: str):
    """Orchestrates sitemap generation for a crawl job."""
    try:
        job = CrawlJob.objects.get(id=job_id)
        generator = SitemapGenerator(job)
        xml_content = generator.generate_xml()
        
        file_name = f"{job.id}_sitemap.xml"
        job.generated_sitemap.save(file_name, ContentFile(xml_content), save=True)
        
        logger.info(f"Sitemap generated for job {job_id}")
    except CrawlJob.DoesNotExist:
        logger.error(f"CrawlJob {job_id} not found for sitemap generation")
    except Exception as e:
        logger.error(f"Error generating sitemap for job {job_id}: {e}")
