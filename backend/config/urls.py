from django.contrib import admin
from django.urls import path, include
from ninja import NinjaAPI
from apps.crawler.api import router as crawler_router
from apps.users.api import router as users_router

from ninja.security import SessionAuth

api = NinjaAPI(title="Service Platform API", auth=SessionAuth())

# Connecting the individual services
api.add_router("/crawler/", crawler_router)
api.add_router("/users/", users_router)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", api.urls),
    path("accounts/", include("allauth.urls")),
]
