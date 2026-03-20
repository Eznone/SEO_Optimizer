from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
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

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT if hasattr(settings, 'STATIC_ROOT') else settings.BASE_DIR / 'static')
