from django.db import models
import uuid

class CrawlJob(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    target_url = models.URLField()
    target_keywords = models.JSONField(default=list, blank=True)
    status = models.CharField(max_length=20, default='pending') # pending, processing, completed, failed
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    total_pages_crawled = models.IntegerField(default=0)
    has_llms_txt = models.BooleanField(default=False)
    generated_llms_txt = models.FileField(upload_to='llms_txts/', null=True, blank=True)
    generated_sitemap = models.FileField(upload_to='sitemaps/', null=True, blank=True)

    def __str__(self):
        return f"Crawl Job for {self.target_url} - {self.status}"

class CrawledPage(models.Model):
    job = models.ForeignKey(CrawlJob, on_delete=models.CASCADE, related_name='pages')
    url = models.URLField(max_length=2000)
    status_code = models.IntegerField(null=True, blank=True)
    
    # Standard SEO Metadata
    title = models.CharField(max_length=500, null=True, blank=True)
    meta_description = models.TextField(null=True, blank=True)
    h1 = models.CharField(max_length=500, null=True, blank=True)
    canonical_url = models.URLField(max_length=2000, null=True, blank=True)
    is_noindex = models.BooleanField(default=False)
    
    # Extracted Data
    raw_html = models.TextField(null=True, blank=True)
    extracted_text = models.TextField(null=True, blank=True)
    json_ld_payload = models.JSONField(null=True, blank=True)
    metadata_headers = models.JSONField(null=True, blank=True)
    
    content_hash = models.CharField(max_length=64, null=True, blank=True)
    depth = models.IntegerField(default=0)
    priority = models.FloatField(default=0.5)
    
    class Meta:
        unique_together = ('job', 'url')

    def __str__(self):
        return f"Page {self.url} (Job {self.job_id})"

class Link(models.Model):
    job = models.ForeignKey(CrawlJob, on_delete=models.CASCADE, related_name='links')
    source_page = models.ForeignKey(CrawledPage, on_delete=models.CASCADE, related_name='outgoing_links', null=True, blank=True)
    target_url = models.URLField(max_length=2000)
    anchor_text = models.CharField(max_length=500, null=True, blank=True)
    is_dofollow = models.BooleanField(default=True)
    is_broken = models.BooleanField(default=False)
    redirect_chain_length = models.IntegerField(default=0)

    def __str__(self):
        source = self.source_page.url if self.source_page else "External/Initial"
        return f"Link from {source} to {self.target_url}"

class AuditIssue(models.Model):
    ISSUE_TYPES = [
        ('orphan', 'Orphan Page'),
        ('broken_link', 'Broken Link'),
        ('canonical_conflict', 'Canonical Conflict'),
        ('redirect_chain', 'Redirect Chain'),
        ('noindex', 'Noindex in Sitemap'),
        ('duplicate_content', 'Duplicate Content'),
        ('missing_sitemap', 'Missing from Sitemap'),
        ('schema_missing_coordinates', 'Missing Coordinates (LocalBusiness)'),
        ('schema_missing_sameas', 'Missing sameAs (Organization)'),
        ('schema_drift', 'Schema-to-Content Mismatch'),
        ('eeat_missing_signal', 'Missing E-E-A-T Signal'),
        ('keyword_missing', 'Target Keyword Missing'),
        ('low_keyword_density', 'Low Keyword Density'),
    ]
    SEVERITY_CHOICES = [
        ('high', 'High'),
        ('medium', 'Medium'),
        ('low', 'Low'),
    ]

    job = models.ForeignKey(CrawlJob, on_delete=models.CASCADE, related_name='issues')
    page = models.ForeignKey(CrawledPage, on_delete=models.CASCADE, related_name='issues', null=True, blank=True)
    issue_type = models.CharField(max_length=50, choices=ISSUE_TYPES)
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES)
    description = models.TextField()

    def __str__(self):
        return f"{self.get_severity_display()} - {self.get_issue_type_display()} on {self.page.url if self.page else 'Site'}"

class Recommendation(models.Model):
    job = models.ForeignKey(CrawlJob, on_delete=models.CASCADE, related_name='recommendations')
    priority = models.IntegerField(default=1) # 1 highest
    action_required = models.CharField(max_length=255)
    business_impact = models.TextField()
    affected_pages_count = models.IntegerField(default=0)

    def __str__(self):
        return f"Recommendation: {self.action_required} (Job {self.job_id})"