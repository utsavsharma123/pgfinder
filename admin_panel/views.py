from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.utils import timezone

from accounts.models import KYCDocument
from accounts.serializers import UserProfileSerializer, KYCDocumentSerializer
from listings.models import Listing
from listings.serializers import ListingDetailSerializer

User = get_user_model()


class IsAdminUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and (request.user.is_staff or request.user.user_type == 'admin')


@extend_schema(tags=['Admin'])
class PendingVerificationsView(generics.ListAPIView):
    """List owners with pending KYC verification (admin only)."""
    serializer_class = KYCDocumentSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        return KYCDocument.objects.filter(is_verified=False).select_related('user')


@extend_schema(tags=['Admin'])
class VerifyOwnerView(APIView):
    """Approve or reject an owner's KYC verification (admin only)."""
    permission_classes = [IsAdminUser]

    def patch(self, request, user_id):
        action = request.data.get('action')  # 'approve' or 'reject'
        reason = request.data.get('reason', '')

        user = get_object_or_404(User, pk=user_id, user_type='owner')

        if action == 'approve':
            user.is_kyc_verified = True
            user.save()
            KYCDocument.objects.filter(user=user).update(is_verified=True, verified_at=timezone.now())
            return Response({'detail': f'{user.full_name} verified successfully.'})
        elif action == 'reject':
            KYCDocument.objects.filter(user=user).update(rejection_reason=reason)
            return Response({'detail': f'Verification rejected for {user.full_name}.'})
        else:
            return Response({'detail': 'action must be "approve" or "reject".'}, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(tags=['Admin'])
class ListingModerationView(APIView):
    """Suspend or reinstate a listing (admin only)."""
    permission_classes = [IsAdminUser]

    def patch(self, request, pk):
        listing = get_object_or_404(Listing, pk=pk)
        new_status = request.data.get('status')
        if new_status not in [Listing.Status.ACTIVE, Listing.Status.SUSPENDED]:
            return Response({'detail': 'Invalid status.'}, status=status.HTTP_400_BAD_REQUEST)
        listing.status = new_status
        listing.save()
        return Response({'detail': f'Listing status updated to {new_status}.'})


@extend_schema(tags=['Admin'])
class PlatformStatsView(APIView):
    """High-level platform stats for admin dashboard."""
    permission_classes = [IsAdminUser]

    def get(self, request):
        from listings.models import Listing
        from inquiries.models import Inquiry
        return Response({
            'total_users': User.objects.count(),
            'total_tenants': User.objects.filter(user_type='tenant').count(),
            'total_owners': User.objects.filter(user_type='owner').count(),
            'verified_owners': User.objects.filter(user_type='owner', is_kyc_verified=True).count(),
            'total_listings': Listing.objects.count(),
            'active_listings': Listing.objects.filter(status='active').count(),
            'total_inquiries': Inquiry.objects.count(),
            'pending_kyc': KYCDocument.objects.filter(is_verified=False).count(),
        })
