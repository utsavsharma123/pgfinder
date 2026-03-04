from rest_framework import serializers, generics, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'notif_type', 'title', 'body', 'is_read', 'metadata', 'created_at']
        read_only_fields = ['id', 'notif_type', 'title', 'body', 'metadata', 'created_at']


@extend_schema(tags=['Notifications'])
class NotificationListView(generics.ListAPIView):
    """List all notifications for the authenticated user."""
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)


@extend_schema(tags=['Notifications'])
class NotificationMarkReadView(APIView):
    """Mark all notifications as read."""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
        return Response({'detail': 'All notifications marked as read.'})


@extend_schema(tags=['Notifications'])
class NotificationMarkOneReadView(APIView):
    """Mark a single notification as read."""
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, pk):
        try:
            notif = Notification.objects.get(pk=pk, user=request.user)
            notif.is_read = True
            notif.save()
            return Response(NotificationSerializer(notif).data)
        except Notification.DoesNotExist:
            return Response({'detail': 'Not found.'}, status=404)
