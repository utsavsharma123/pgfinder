from django.urls import path
from .views import PresignedUploadView

urlpatterns = [
    path('photo/', PresignedUploadView.as_view(), name='upload-photo'),
]
