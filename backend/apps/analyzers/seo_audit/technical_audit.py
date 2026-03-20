import requests
import logging
from apps.crawler.models import CrawlJob, CrawledPage, AuditIssue, Recommendation, Link
from django.db.models import Count
from urllib.parse import urlparse
import httpx
import os
import json

logger = logging.getLogger(__name__)

class TechnicalAuditAnalyzer:
    GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
    MODEL = "llama-3.3-70b-versatile"

    def __init__(self, job: CrawlJob):
        self.job = job
        self.api_key = self._get_user_api_key()

    def _get_user_api_key(self):
        if self.job.user and hasattr(self.job.user, 'profile'):
            return self.job.user.profile.groq_api_key
        return os.getenv("GROQ_API_KEY")

    def analyze(self):
        self.check_internal_link_depth()
        self.check_ai_bot_management()
        self.check_toxic_outgoing_links()
        self.check_mobile_readiness()
        self.check_performance_proxies()
        self.generate_recommendations()

    def check_performance_proxies(self):
        """Check for patterns that might cause poor INP (e.g., excessive scripts)."""
        pages = CrawledPage.objects.filter(job=self.job, status_code=200)
        for page in pages:
            if page.raw_html:
                # Count <script> tags
                script_count = page.raw_html.lower().count('<script')
                if script_count > 20:
                    AuditIssue.objects.create(
                        job=self.job,
                        page=page,
                        issue_type='mobile_parity_issue', # Reusing for now or could add inp_slow
                        severity='medium',
                        description=f"High script count ({script_count} scripts) detected. Excessive JavaScript can lead to poor Interaction to Next Paint (INP) scores."
                    )

    def check_internal_link_depth(self):
        """No critical page should be more than 3 clicks from the homepage."""
        deep_pages = CrawledPage.objects.filter(job=self.job, depth__gt=3)
        count = deep_pages.count()
        
        if count > 0:
            for page in deep_pages:
                AuditIssue.objects.create(
                    job=self.job,
                    page=page,
                    issue_type='high_link_depth',
                    severity='medium',
                    description=f"This page is {page.depth} clicks away from the homepage. Critical content should be within 3 clicks."
                )

    def check_ai_bot_management(self):
        """Check robots.txt for AI crawler blocks."""
        parsed_url = urlparse(self.job.target_url)
        robots_url = f"{parsed_url.scheme}://{parsed_url.netloc}/robots.txt"
        
        try:
            response = requests.get(robots_url, timeout=10)
            if response.status_code == 200:
                content = response.text.lower()
                ai_bots = ['gptbot', 'google-extended', 'ccbot', 'anthropic-ai', 'claudebot']
                blocked_bots = []
                
                for bot in ai_bots:
                    if f"user-agent: {bot}" in content:
                        # Check if it's followed by Disallow: /
                        # This is a bit simplified but works for common patterns
                        bot_section = content.split(f"user-agent: {bot}")[1].split("user-agent:")[0]
                        if "disallow: /" in bot_section and "allow: /" not in bot_section:
                            blocked_bots.append(bot)
                
                if blocked_bots:
                    AuditIssue.objects.create(
                        job=self.job,
                        issue_type='ai_bot_blocked',
                        severity='low',
                        description=f"Your robots.txt is blocking AI crawlers: {', '.join(blocked_bots)}. This may prevent your site from appearing in AI summaries and search experiences."
                    )
            elif response.status_code == 404:
                # No robots.txt, default is allowed, which is good for AI bots usually
                pass
        except Exception as e:
            logger.error(f"Error checking robots.txt: {e}")

    def check_toxic_outgoing_links(self):
        """Use AI to identify potentially toxic outgoing links."""
        if not self.api_key:
            return

        # Get external links
        external_links = Link.objects.filter(job=self.job).exclude(target_url__icontains=urlparse(self.job.target_url).netloc).values('target_url').annotate(count=Count('id'))[:50]
        
        if not external_links:
            return

        links_to_check = [l['target_url'] for l in external_links]
        
        prompt = f"""
        Analyze the following list of outgoing links from a website. 
        Identify if any of these appear to be 'link farms', spammy directories, or high-risk 'bad neighborhoods' for SEO in 2026.
        
        Links:
        {json.dumps(links_to_check)}
        
        Return the result ONLY in JSON format:
        {{
            "toxic_links": [
                {{"url": "toxic-url.com", "reason": "Known link farm", "severity": "high"}}
            ]
        }}
        If none are toxic, return an empty list for "toxic_links".
        """

        try:
            with httpx.Client() as client:
                response = client.post(
                    self.GROQ_API_URL,
                    headers={"Authorization": f"Bearer {self.api_key}"},
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
                    
                    for item in result.get('toxic_links', []):
                        # Find a link object to attach this to
                        link_obj = Link.objects.filter(job=self.job, target_url=item['url']).first()
                        AuditIssue.objects.create(
                            job=self.job,
                            page=link_obj.source_page if link_obj else None,
                            issue_type='toxic_link',
                            severity=item.get('severity', 'medium'),
                            description=f"Outgoing link to {item['url']} flagged as toxic: {item['reason']}."
                        )
        except Exception as e:
            logger.error(f"Error checking toxic links: {e}")

    def check_mobile_readiness(self):
        """Basic check for mobile-first optimization (Viewport meta tag)."""
        pages = CrawledPage.objects.filter(job=self.job, status_code=200)
        for page in pages:
            if page.raw_html:
                if 'viewport' not in page.raw_html.lower():
                    AuditIssue.objects.create(
                        job=self.job,
                        page=page,
                        issue_type='mobile_parity_issue',
                        severity='high',
                        description="Missing viewport meta tag. This is critical for mobile-first indexing and user experience."
                    )

    def generate_recommendations(self):
        # Recommendations for Link Depth
        depth_issues = AuditIssue.objects.filter(job=self.job, issue_type='high_link_depth').count()
        if depth_issues > 0:
            Recommendation.objects.get_or_create(
                job=self.job,
                action_required="Flat Site Architecture",
                defaults={
                    'priority': 2,
                    'business_impact': "Search engines and users prefer a flatter architecture where content is easily discoverable within 3 clicks. Deeply nested pages receive less crawl budget and 'link juice'.",
                    'affected_pages_count': depth_issues
                }
            )

        # AI Bot Recommendations
        if AuditIssue.objects.filter(job=self.job, issue_type='ai_bot_blocked').exists():
            Recommendation.objects.get_or_create(
                job=self.job,
                action_required="Optimize for AI Search (SGE/Perplexity)",
                defaults={
                    'priority': 1,
                    'business_impact': "By unblocking AI bots, your content can be indexed and summarized by LLM-powered search engines, driving traffic from conversational search queries.",
                    'affected_pages_count': 1
                }
            )

def process_technical_audit(job_id: str):
    try:
        job = CrawlJob.objects.get(id=job_id)
        analyzer = TechnicalAuditAnalyzer(job)
        analyzer.analyze()
        logger.info(f"Technical audit completed for job {job_id}")
    except CrawlJob.DoesNotExist:
        logger.error(f"CrawlJob {job_id} not found")
    except Exception as e:
        logger.error(f"Error in technical audit: {e}")
