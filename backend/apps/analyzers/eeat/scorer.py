import httpx
import logging
import os
import json
from apps.crawler.models import CrawlJob, CrawledPage, AuditIssue, Recommendation
from django.conf import settings

logger = logging.getLogger(__name__)

class EEATScorer:
    GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
    MODEL = "llama-3.3-70b-versatile"

    def __init__(self, job: CrawlJob):
        self.job = job
        self.api_key = self._get_user_api_key()

    def _get_user_api_key(self):
        """Fetches the Groq API key from the user's profile."""
        if self.job.user and hasattr(self.job.user, 'profile'):
            return self.job.user.profile.groq_api_key
        # Fallback to env var for legacy/system jobs (optional)
        return os.getenv("GROQ_API_KEY")

    def score_all_pages(self, limit=10):
        """Scores pages for E-E-A-T and Conversational Structure."""
        pages = CrawledPage.objects.filter(job=self.job, status_code=200).exclude(extracted_text__isnull=True).exclude(extracted_text="")
        
        # Limit scoring to top pages to avoid API costs/limits
        pages = pages.order_by('-priority')[:limit]
        
        for page in pages:
            self._score_page(page)
        
        self.generate_recommendations()

    def _score_page(self, page: CrawledPage):
        if not self.api_key or self.api_key == "your_groq_api_key_here":
            logger.warning("GROQ_API_KEY not set, skipping E-E-A-T scoring.")
            return

        prompt = f"""
        Analyze the following web page content for 2026 SEO standards (E-E-A-T and Conversational Search optimization).
        
        Content:
        {page.extracted_text[:4000]}
        
        Evaluate based on:
        1. Conversational Structure: Does it answer questions quickly? (0-10)
        2. E-E-A-T: Are there author credentials, expert bios, or verifiable claims? (0-10)
        3. Extractability: Is the information easy for an LLM to extract (e.g., lists, clear headers)? (0-10)
        
        Return the result ONLY in JSON format like this:
        {{
            "conversational_score": 8,
            "eeat_score": 7,
            "extractability_score": 9,
            "issues": ["No clear author bio", "Missing direct answer to main query"],
            "summary": "Short summary of findings"
        }}
        """

        try:
            with httpx.Client() as client:
                response = client.post(
                    self.GROQ_API_URL,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": self.MODEL,
                        "messages": [{"role": "user", "content": prompt}],
                        "response_format": {"type": "json_object"}
                    },
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    result = json.loads(data['choices'][0]['message']['content'])
                    
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
                else:
                    logger.error(f"Groq API error: {response.status_code} - {response.text}")
                    
        except Exception as e:
            logger.error(f"Error scoring page {page.url} with Groq: {e}")

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
