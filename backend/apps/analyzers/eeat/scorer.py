import logging
import json
from apps.crawler.models import CrawlJob, CrawledPage, AuditIssue, Recommendation
from agents.eeat_agent import EEATAgent

logger = logging.getLogger(__name__)

class EEATScorer:
    def __init__(self, job: CrawlJob):
        self.job = job
        self.agent = EEATAgent(user=job.user)

    def score_all_pages(self, limit=10):
        """Scores pages for E-E-A-T and Conversational Structure."""
        pages = CrawledPage.objects.filter(job=self.job, status_code=200).exclude(extracted_text__isnull=True).exclude(extracted_text="")
        
        # Limit scoring to top pages to avoid API costs/limits
        pages = pages.order_by('-priority')[:limit]
        
        for page in pages:
            self._score_page(page)
        
        self.generate_recommendations()

    def _score_page(self, page: CrawledPage):
        if not self.agent.api_key:
            logger.warning("GROQ_API_KEY not set, skipping E-E-A-T scoring.")
            return

        result = self.agent.analyze_page(page.extracted_text)
        
        if result:
            try:
                # Store results or create issues
                for issue_desc in result.get('issues', []):
                    AuditIssue.objects.create(
                        job=self.job,
                        page=page,
                        issue_type='eeat_missing_signal',
                        severity='medium',
                        description=issue_desc
                    )
                
                logger.info(f"E-E-A-T scored for {page.url}")
            except Exception as e:
                logger.error(f"Error processing agent result for {page.url}: {e}")
        else:
            logger.error(f"Agent failed to score page {page.url}")

    def generate_recommendations(self):
        """Summarizes E-E-A-T issues into actionable recommendations."""
        issue_counts = AuditIssue.objects.filter(job=self.job, issue_type='eeat_missing_signal').count()
        
        if issue_counts > 0:
            Recommendation.objects.get_or_create(
                job=self.job,
                action_required="Enhance E-E-A-T and Conversational Readiness",
                defaults={
                    'priority': 1,
                    'business_impact': "Modern generative search engines require strong signals of expertise and authority (E-E-A-T) and content that is easy to summarize for AI answers. Improving this increases the likelihood of being cited in AI-generated search results.",
                    'affected_pages_count': issue_counts
                }
            )

def process_eeat_scoring(job_id: str):
    """Orchestrates E-E-A-T scoring for a crawl job."""
    try:
        job = CrawlJob.objects.get(id=job_id)
        scorer = EEATScorer(job)
        scorer.score_all_pages()
        logger.info(f"E-E-A-T scoring completed for job {job_id}")
    except CrawlJob.DoesNotExist:
        logger.error(f"CrawlJob {job_id} not found for E-E-A-T scoring")
    except Exception as e:
        logger.error(f"Error in E-E-A-T scoring for job {job_id}: {e}")
