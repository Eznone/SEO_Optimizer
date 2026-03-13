from django.db import models
import uuid

class SitemapJob(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    target_url = models.URLField()
    status = models.CharField(max_length=20, default='pending') # pending, processing, completed, failed
    sitemap_file = models.FileField(upload_to='sitemaps/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Sitemap for {self.target_url} - {self.status}"