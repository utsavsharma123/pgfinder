from rest_framework import generics, serializers, permissions
from drf_spectacular.utils import extend_schema
from .models import ChatRoom, Message
from inquiries.models import Inquiry


class MessageSerializer(serializers.ModelSerializer):
    sender_name = serializers.CharField(source='sender.full_name', read_only=True)

    class Meta:
        model = Message
        fields = ['id', 'sender_name', 'content', 'attachment_url', 'is_read', 'created_at']


class ChatRoomSerializer(serializers.ModelSerializer):
    messages = MessageSerializer(many=True, read_only=True)
    inquiry_id = serializers.IntegerField(source='inquiry.id', read_only=True)

    class Meta:
        model = ChatRoom
        fields = ['id', 'inquiry_id', 'messages', 'created_at']


@extend_schema(tags=['Chat'])
class ChatRoomView(generics.RetrieveAPIView):
    """
    Get chat room and message history for an inquiry.
    Room is created automatically when inquiry is accepted.
    WebSocket: ws://host/ws/chat/{room_id}/
    """
    serializer_class = ChatRoomSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        inquiry_id = self.kwargs['inquiry_id']
        user = self.request.user
        inquiry = Inquiry.objects.get(
            pk=inquiry_id
        )
        if user not in [inquiry.tenant, inquiry.listing.owner]:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied('Access denied.')
        room, _ = ChatRoom.objects.get_or_create(inquiry=inquiry)
        return room
