from ninja import Schema
from pydantic import AnyHttpUrl
from typing import Optional, List
import uuid
from datetime import datetime

class CrawlJobCreate(Schema):
    target_url: AnyHttpUrl
    target_keywords: Optional[List[str]] = []

class CrawlJobResponse(Schema):
    id: uuid.UUID
    target_url: str
    status: str
    total_pages_crawled: int
    has_llms_txt: bool
    llms_txt_url: Optional[str] = None
    sitemap_url: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None

class AuditIssueSchema(Schema):
    id: int
    url: Optional[str] = None
    issue_type: str
    severity: str
    description: str

    @staticmethod
    def resolve_url(obj):
        return obj.page.url if obj.page else None

class RecommendationSchema(Schema):
    id: int
    priority: int
    action_required: str
    business_impact: str
    affected_pages_count: int

class CrawledPageSchema(Schema):
    id: int
    url: str
    status_code: Optional[int]
    title: Optional[str]
    is_noindex: bool
    depth: int
    priority: float
