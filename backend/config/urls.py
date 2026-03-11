from django.contrib import admin
from django.urls import path
from ninja import NinjaAPI
from apps.sitemaps.api import router as sitemap_router

api = NinjaAPI(title="Service Platform API")

# Connecting the individual services
api.add_router("/sitemaps/", sitemap_router)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", api.urls),
]