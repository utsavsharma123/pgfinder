from django.urls import path
from .views import PendingVerificationsView, VerifyOwnerView, ListingModerationView, PlatformStatsView

urlpatterns = [
    path('pending-verifications/', PendingVerificationsView.as_view(), name='admin-pending-verifications'),
    path('verify-owner/<int:user_id>/', VerifyOwnerView.as_view(), name='admin-verify-owner'),
    path('listings/<int:pk>/moderate/', ListingModerationView.as_view(), name='admin-listing-moderate'),
    path('stats/', PlatformStatsView.as_view(), name='admin-stats'),
]
