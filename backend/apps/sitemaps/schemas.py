from ninja import Schema
from uuid import UUID
from datetime import datetime
from typing import Optional, List

class SitemapCreateSchema(Schema):
    target_url: str

class SitemapResponseSchema(Schema):
    id: UUID
    target_url: str
    status: str
    created_at: datetime
    completed_at: Optional[datetime] = None
    total_pages_crawled: int
    total_issues_found: int
    sitemap_url: Optional[str] = None

class RecommendationSchema(Schema):
    id: int
    priority: int
    action_required: str
    business_impact: str
    affected_pages_count: int

class IssueSchema(Schema):
    id: int
    issue_type: str
    severity: str
    description: str
    page_url: Optional[str] = None

    @staticmethod
    def resolve_page_url(obj):
        return obj.page.url if obj.page else None

class PageSchema(Schema):
    id: int
    url: str
    status_code: Optional[int]
    title: Optional[str]
    is_noindex: bool
