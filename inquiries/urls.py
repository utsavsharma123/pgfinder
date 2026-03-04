from django.urls import path
from .views import InquiryListCreateView, InquiryDetailView, InquiryStatusUpdateView

urlpatterns = [
    path('', InquiryListCreateView.as_view(), name='inquiry-list'),
    path('<int:pk>/', InquiryDetailView.as_view(), name='inquiry-detail'),
    path('<int:pk>/status/', InquiryStatusUpdateView.as_view(), name='inquiry-status'),
]
