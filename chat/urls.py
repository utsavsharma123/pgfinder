from django.urls import path
from .views import ChatRoomView

urlpatterns = [
    path('room/<int:inquiry_id>/', ChatRoomView.as_view(), name='chat-room'),
]
