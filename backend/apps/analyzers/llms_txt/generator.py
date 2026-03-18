import requests
from urllib.parse import urlparse, urljoin
from apps.crawler.models import CrawlJob, CrawledPage
from django.core.files.base import ContentFile
from django.conf import settings
import os

def check_existing_llms_txt(base_url: str) -> bool:
    """Checks if llms.txt already exists at the target URL root."""
    try:
        url = urljoin(base_url, '/llms.txt')
        response = requests.head(url, timeout=5.0, allow_redirects=True)
        return response.status_code == 200
    except requests.RequestException:
        return False

def generate_llms_txt(job: CrawlJob) -> str:
    """Generates llms.txt content based on crawled pages."""
    domain = urlparse(job.target_url).netloc
    
    lines = [f"# {domain}", ""]
    lines.append(f"> Auto-generated llms.txt for AI crawlers.")
    lines.append("")
    lines.append("## Important Pages")
    
    # Get all successful pages, sort by depth (proxy for priority)
    pages = CrawledPage.objects.filter(job=job, status_code=200).order_by('depth')[:50]
    
    for page in pages:
        title = page.title or page.url
        desc = page.meta_description or "No description available."
        lines.append(f"- [{title}]({page.url}): {desc}")
        
    return "\n".join(lines)

def process_llms_txt_job(job_id: str):
    """Orchestrates the llms.txt detection and generation."""
    try:
        job = CrawlJob.objects.get(id=job_id)
        
        # 1. Detect existing
        if check_existing_llms_txt(job.target_url):
            job.has_llms_txt = True
            job.save()
            return
            
        # 2. Generate if not exists
        content = generate_llms_txt(job)
        
        # Save to the model's FileField
        file_name = f"{job.id}_llms.txt"
        job.generated_llms_txt.save(file_name, ContentFile(content.encode('utf-8')), save=True)
        
    except CrawlJob.DoesNotExist:
        pass
