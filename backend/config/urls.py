from django.contrib import admin
from django.urls import path
from ninja import NinjaAPI
from apps.sitemaps.api import router as sitemap_router
from apps.seo_audit.api import router as seo_audit_router
from apps.crawler.api import router as crawler_router

api = NinjaAPI(title="Service Platform API")

# Connecting the individual services
api.add_router("/sitemaps/", sitemap_router)
api.add_router("/seo-audit/", seo_audit_router)
api.add_router("/crawler/", crawler_router)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", api.urls),
]