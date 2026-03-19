import re
import logging
from apps.crawler.models import CrawlJob, CrawledPage, AuditIssue, Recommendation
from django.db.models import Count

logger = logging.getLogger(__name__)

class KeywordAnalyzer:
    def __init__(self, job: CrawlJob):
        self.job = job
        self.target_keywords = job.target_keywords or []

    def analyze(self):
        if not self.target_keywords:
            return

        pages = CrawledPage.objects.filter(job=self.job, status_code=200)
        for page in pages:
            self._analyze_page(page)
        
        self.generate_recommendations()

    def _analyze_page(self, page: CrawledPage):
        if not page.extracted_text:
            return

        page_text = page.extracted_text.lower()
        title = (page.title or "").lower()
        h1 = (page.h1 or "").lower()
        
        words = page_text.split()
        total_words = len(words)

        for kw in self.target_keywords:
            kw_lower = kw.lower()
            # Count occurrences using regex for word boundaries
            matches = re.findall(rf'\b{re.escape(kw_lower)}\b', page_text)
            count = len(matches)

            if count == 0:
                AuditIssue.objects.create(
                    job=self.job,
                    page=page,
                    issue_type='keyword_missing',
                    severity='medium',
                    description=f"Target keyword '{kw}' is completely missing from the page content."
                )
            else:
                # Check for presence in critical tags
                missing_in = []
                if kw_lower not in title:
                    missing_in.append("title")
                if kw_lower not in h1:
                    missing_in.append("H1 tag")
                
                if missing_in:
                    AuditIssue.objects.create(
                        job=self.job,
                        page=page,
                        issue_type='keyword_missing',
                        severity='low',
                        description=f"Target keyword '{kw}' is present in content but missing from: {', '.join(missing_in)}."
                    )

                # Density check (very basic)
                density = (count / total_words) * 100 if total_words > 0 else 0
                if density < 0.5: # 0.5% threshold for example
                    AuditIssue.objects.create(
                        job=self.job,
                        page=page,
                        issue_type='low_keyword_density',
                        severity='low',
                        description=f"Target keyword '{kw}' has a low density ({density:.2f}%). Consider natural usage in more sections."
                    )

    def generate_recommendations(self):
        issue_counts = AuditIssue.objects.filter(job=self.job, issue_type__in=['keyword_missing', 'low_keyword_density']).values('issue_type').annotate(count=Count('id'))
        
        for item in issue_counts:
            issue_type = item['issue_type']
            count = item['count']
            
            if issue_type == 'keyword_missing':
                Recommendation.objects.get_or_create(
                    job=self.job,
                    action_required="Optimize Pages for Target Keywords",
                    defaults={
                        'priority': 2,
                        'business_impact': "Pages missing their target keywords in critical areas like the Title or H1 are significantly less likely to rank for those terms in search results.",
                        'affected_pages_count': count
                    }
                )
            elif issue_type == 'low_keyword_density':
                Recommendation.objects.get_or_create(
                    job=self.job,
                    action_required="Improve Keyword Relevance and Density",
                    defaults={
                        'priority': 3,
                        'business_impact': "While 'keyword stuffing' should be avoided, ensure that your target topics are mentioned enough to signal relevance to search engines.",
                        'affected_pages_count': count
                    }
                )

def process_keyword_analysis(job_id: str):
    """Orchestrates keyword analysis for a crawl job."""
    try:
        job = CrawlJob.objects.get(id=job_id)
        analyzer = KeywordAnalyzer(job)
        analyzer.analyze()
        logger.info(f"Keyword analysis completed for job {job_id}")
    except CrawlJob.DoesNotExist:
        logger.error(f"CrawlJob {job_id} not found for keyword analysis")
    except Exception as e:
        logger.error(f"Error in keyword analysis for job {job_id}: {e}")
