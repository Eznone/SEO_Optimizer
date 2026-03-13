from ninja import Schema
from uuid import UUID
from datetime import datetime
from typing import Optional

class SitemapCreateSchema(Schema):
    target_url: str

class SitemapResponseSchema(Schema):
    id: UUID
    target_url: str
    status: str
    created_at: datetime
    sitemap_url: Optional[str] = None