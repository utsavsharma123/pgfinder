"""
PG Finder — Root URL configuration
Swagger UI available at /api/docs/
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)

urlpatterns = [
    # Django Admin
    path('django-admin/', admin.site.urls),

    # ── OpenAPI Schema & Docs ──────────────────────────────────────────────────
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

    # ── API v1 Routes ──────────────────────────────────────────────────────────
    path('api/auth/', include('accounts.urls')),
    path('api/listings/', include('listings.urls')),
    path('api/search/', include('search.urls')),
    path('api/inquiries/', include('inquiries.urls')),
    path('api/upload/', include('media.urls')),
    path('api/notifications/', include('notifications.urls')),
    path('api/chat/', include('chat.urls')),
    path('api/subscriptions/', include('subscriptions.urls')),
    path('api/admin-panel/', include('admin_panel.urls')),
    path('api/profile/', include('accounts.profile_urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
