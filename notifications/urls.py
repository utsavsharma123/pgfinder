from django.urls import path
from .views import NotificationListView, NotificationMarkReadView, NotificationMarkOneReadView

urlpatterns = [
    path('', NotificationListView.as_view(), name='notification-list'),
    path('mark-all-read/', NotificationMarkReadView.as_view(), name='notification-mark-all-read'),
    path('<int:pk>/read/', NotificationMarkOneReadView.as_view(), name='notification-mark-read'),
]
