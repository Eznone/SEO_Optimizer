from pydantic import BaseModel, AnyHttpUrl
from typing import Optional
import uuid
from datetime import datetime

class CrawlJobCreate(BaseModel):
    target_url: AnyHttpUrl

class CrawlJobResponse(BaseModel):
    id: uuid.UUID
    target_url: str
    status: str
    total_pages_crawled: int
    has_llms_txt: bool
    llms_txt_url: Optional[str] = None
    sitemap_url: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None

class AuditIssueSchema(BaseModel):
    id: int
    url: Optional[str] = None
    issue_type: str
    severity: str
    description: str

    @staticmethod
    def resolve_url(obj):
        return obj.page.url if obj.page else None

class RecommendationSchema(BaseModel):
    id: int
    priority: int
    action_required: str
    business_impact: str
    affected_pages_count: int
