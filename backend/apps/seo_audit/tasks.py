from celery import shared_task
from .services import perform_seo_analysis

@shared_task(bind=True)
def run_seo_audit_task(self, url: str, target_keywords: list = None):
    # This runs in the background
    result = perform_seo_analysis(url)
    
    # You could save to a Database Model here:
    # AuditResult.objects.create(url=url, data=result)
    
    return result