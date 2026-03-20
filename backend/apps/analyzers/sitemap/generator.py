import xml.etree.ElementTree as ET
from datetime import datetime
from apps.crawler.models import CrawlJob, CrawledPage, AuditIssue, Recommendation, Link
from apps.crawler.utils import save_file_safely
from django.db.models import Count
import logging

logger = logging.getLogger(__name__)

class SitemapGenerator:
    def __init__(self, job: CrawlJob, changefreq: str = "weekly"):
        self.job = job
        self.changefreq = changefreq
        self.generation_time = datetime.now().strftime('%Y-%m-%d')

    def generate_xml(self) -> bytes:
        # Exclude noindex pages from sitemap
        pages = CrawledPage.objects.filter(job=self.job, status_code=200, is_noindex=False)
        urlset = ET.Element("urlset", xmlns="http://www.sitemaps.org/schemas/sitemap/0.9")

        for page in pages:
            url_el = ET.SubElement(urlset, "url")
            ET.SubElement(url_el, "loc").text = page.url
            ET.SubElement(url_el, "lastmod").text = self.generation_time
            ET.SubElement(url_el, "changefreq").text = self.changefreq
            ET.SubElement(url_el, "priority").text = str(page.priority)

        return ET.tostring(urlset, encoding='utf-8', method='xml', xml_declaration=True)

    def validate_and_recommend(self):
        """Analyzes crawl results for sitemap and link-related issues."""
        self._check_broken_links()
        self._check_noindex_pages()
        self._check_orphan_pages()
        self.generate_recommendations()

    def _check_broken_links(self):
        broken_links = Link.objects.filter(job=self.job, is_broken=True)
        for link in broken_links:
            AuditIssue.objects.get_or_create(
                job=self.job,
                page=link.source_page,
                issue_type='broken_link',
                defaults={
                    'severity': 'high',
                    'description': f"Broken link found pointing to {link.target_url}"
                }
            )

    def _check_noindex_pages(self):
        noindex_pages = CrawledPage.objects.filter(job=self.job, is_noindex=True)
        for page in noindex_pages:
            AuditIssue.objects.get_or_create(
                job=self.job,
                page=page,
                issue_type='noindex',
                defaults={
                    'severity': 'medium',
                    'description': "Page is marked 'noindex' and was excluded from the sitemap."
                }
            )

    def _check_orphan_pages(self):
        # A better 'orphan' definition here might be pages with very few incoming internal links.
        # But Link model uses target_url as string, so we'd need a subquery or python-side check.
        # For now, we skip this to ensure stability.
        pass

    def generate_recommendations(self):
        issue_counts = AuditIssue.objects.filter(job=self.job).values('issue_type').annotate(count=Count('id'))
        
        for item in issue_counts:
            issue_type = item['issue_type']
            count = item['count']
            
            if issue_type == 'broken_link':
                Recommendation.objects.get_or_create(
                    job=self.job,
                    action_required="Fix Broken Internal/External Links",
                    defaults={
                        'priority': 1,
                        'business_impact': "Broken links provide a poor user experience and prevent search engines from crawling your site effectively. They are a strong negative quality signal.",
                        'affected_pages_count': count
                    }
                )
            elif issue_type == 'noindex':
                Recommendation.objects.get_or_create(
                    job=self.job,
                    action_required="Review 'noindex' Tags",
                    defaults={
                        'priority': 3,
                        'business_impact': "You have pages marked as 'noindex'. Ensure these are intentional, as they will not appear in search results.",
                        'affected_pages_count': count
                    }
                )

def process_sitemap_job(job_id: str):
    """Orchestrates sitemap generation and validation for a crawl job."""
    try:
        job = CrawlJob.objects.get(id=job_id)
        generator = SitemapGenerator(job)
        
        # Validation and Recommendations
        generator.validate_and_recommend()
        
        # XML Generation
        xml_content = generator.generate_xml()
        
        # Save directly to the database as a string
        job.generated_sitemap = xml_content.decode('utf-8')
        job.save()
        
        logger.info(f"Sitemap generated and validated for job {job_id}")
    except CrawlJob.DoesNotExist:
        logger.error(f"CrawlJob {job_id} not found for sitemap generation")
    except Exception as e:
        logger.error(f"Error generating sitemap for job {job_id}: {e}")
