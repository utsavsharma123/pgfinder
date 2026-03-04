from django.urls import path
from .views import ProfileView, PasswordChangeView, KYCUploadView

urlpatterns = [
    path('', ProfileView.as_view(), name='profile'),
    path('change-password/', PasswordChangeView.as_view(), name='profile-change-password'),
    path('kyc/', KYCUploadView.as_view(), name='profile-kyc'),
]
