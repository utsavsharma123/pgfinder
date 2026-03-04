from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema
from django.shortcuts import get_object_or_404
from django.db.models import Q

from .models import Inquiry
from .serializers import InquirySerializer, InquiryStatusSerializer


@extend_schema(tags=['Inquiries'])
class InquiryListCreateView(generics.ListCreateAPIView):
    """
    GET: List inquiries. Tenants see their own; owners see inquiries for their listings.
    POST: Create an inquiry (tenants only).
    """
    serializer_class = InquirySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.user_type == 'owner':
            return Inquiry.objects.filter(listing__owner=user).select_related('tenant', 'listing')
        return Inquiry.objects.filter(tenant=user).select_related('tenant', 'listing')

    def perform_create(self, serializer):
        if self.request.user.user_type != 'tenant':
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied('Only tenants can send inquiries.')
        inquiry = serializer.save(tenant=self.request.user)
        # Increment listing inquiry count
        inquiry.listing.total_inquiries += 1
        inquiry.listing.save(update_fields=['total_inquiries'])
        # TODO: trigger Celery task to notify owner via WhatsApp/email


@extend_schema(tags=['Inquiries'])
class InquiryDetailView(generics.RetrieveAPIView):
    """Get a specific inquiry detail."""
    serializer_class = InquirySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.user_type == 'owner':
            return Inquiry.objects.filter(listing__owner=user)
        return Inquiry.objects.filter(tenant=user)


@extend_schema(tags=['Inquiries'])
class InquiryStatusUpdateView(APIView):
    """Owner updates inquiry status (accepted/rejected/responded)."""
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, pk):
        if request.user.user_type != 'owner':
            return Response({'detail': 'Only owners can update inquiry status.'}, status=status.HTTP_403_FORBIDDEN)
        inquiry = get_object_or_404(Inquiry, pk=pk, listing__owner=request.user)
        serializer = InquiryStatusSerializer(inquiry, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
