from ninja import Schema
from typing import List, Optional

# Made so we can have a consistent response format for 
# our SEO audit results

class SEOReportSchema(Schema):
    title: Optional[str]
    description: Optional[str]
    keywords_found: List[str]
    load_time_seconds: float
    status: str

class AuditRequest(Schema):
    url: str
    target_keywords: List[str] = []

class AuditResponse(Schema):
    job_id: str
    message: str

class Error(Schema):
    message: str
    error: Optional[str] = None