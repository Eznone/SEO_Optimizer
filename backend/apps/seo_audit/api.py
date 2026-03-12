from ninja import Router

from .tasks import run_seo_audit_task
from .schemas import AuditRequest, AuditResponse, Error
from urllib.parse import urlparse
from django.core.exceptions import ValidationError

router = Router()

@router.post("/audit", response={200: AuditResponse, 400: Error, 500: Error})
def start_audit(request, data: AuditRequest):    # Validating the URL
    try:
        result = urlparse(data.url)
        if not all([result.scheme, result.netloc]):
            raise ValidationError("Invalid URL format")
        if result.scheme not in ['http', 'https']:
            raise ValidationError("Only HTTP and HTTPS URLs are supported")
    except Exception as e:
        return 400, {
            "error": str(e),
            "message": "Invalid URL provided"
        }
    
    # Starting the audit task
    try:
        task = run_seo_audit_task.delay(data.url, data.target_keywords)
        return {
            "message": "SEO audit started",
            "job_id": task.id
        }
    except Exception as e:
        return 500, {
            "error": str(e),
            "message": "Failed to start audit task"
        }
    
@router.get("/audit/{task_id}")
def get_audit_result(request, task_id: str):
    from celery.result import AsyncResult
    try:
        task_result = AsyncResult(task_id)
        if task_result.state == 'PENDING':
            return {
                "status": "Pending",
                "message": "Audit is still in progress"
            }
        elif task_result.state == 'SUCCESS':
            return {
                "status": "Completed",
                "result": task_result.result
            }
        else:
            return {
                "status": task_result.state,
                "message": "Audit failed or was revoked"
            }
    except Exception as e:
        return 500, {
            "error": str(e),
            "message": "Failed to retrieve audit result"
        }