from rest_framework import generics, permissions, status, filters
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, OpenApiParameter
from django.shortcuts import get_object_or_404

from .models import Listing, ListingPhoto, Wishlist
from .serializers import (
    ListingListSerializer,
    ListingDetailSerializer,
    ListingCreateUpdateSerializer,
    ListingPhotoSerializer,
    WishlistSerializer,
)
from .filters import ListingFilter
from .permissions import IsOwnerUser, IsListingOwner


@extend_schema(tags=['Listings'])
class ListingListCreateView(generics.ListCreateAPIView):
    """
    GET: List all active PG listings (public).
    POST: Create a new listing (owners only).
    """
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ListingFilter
    search_fields = ['name', 'city', 'locality', 'address']
    ordering_fields = ['price_single', 'created_at', 'total_views']
    ordering = ['-created_at']

    def get_queryset(self):
        if self.request.user.is_authenticated and self.request.user.user_type == 'owner':
            return Listing.objects.filter(owner=self.request.user)
        return Listing.objects.filter(status='active').select_related('owner').prefetch_related('photos')

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ListingCreateUpdateSerializer
        return ListingListSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsOwnerUser()]
        return [permissions.AllowAny()]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


@extend_schema(tags=['Listings'])
class ListingDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET: Retrieve a listing (public, increments view count).
    PATCH: Update listing (owner only).
    DELETE: Delete listing (owner only).
    """
    queryset = Listing.objects.all().select_related('owner').prefetch_related('photos')

    def get_serializer_class(self):
        if self.request.method in ['PATCH', 'PUT']:
            return ListingCreateUpdateSerializer
        return ListingDetailSerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return [permissions.AllowAny()]
        return [IsListingOwner()]

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        # Increment view count
        Listing.objects.filter(pk=instance.pk).update(total_views=instance.total_views + 1)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


@extend_schema(tags=['Listings'])
class ListingPhotoView(generics.ListCreateAPIView):
    """Upload photos to a listing (max 10). Owner only."""
    serializer_class = ListingPhotoSerializer
    permission_classes = [IsListingOwner]

    def get_queryset(self):
        return ListingPhoto.objects.filter(listing_id=self.kwargs['pk'])

    def perform_create(self, serializer):
        listing = get_object_or_404(Listing, pk=self.kwargs['pk'], owner=self.request.user)
        if listing.photos.count() >= 10:
            from rest_framework.exceptions import ValidationError
            raise ValidationError('Maximum 10 photos allowed per listing.')
        serializer.save(listing=listing)


@extend_schema(tags=['Listings'])
class ListingStatusToggleView(APIView):
    """Toggle listing status between active/occupied. Owner only."""
    permission_classes = [IsListingOwner]

    def patch(self, request, pk):
        listing = get_object_or_404(Listing, pk=pk, owner=request.user)
        new_status = request.data.get('status')
        if new_status not in [Listing.Status.ACTIVE, Listing.Status.OCCUPIED, Listing.Status.DRAFT]:
            return Response({'status': 'Invalid status.'}, status=status.HTTP_400_BAD_REQUEST)
        listing.status = new_status
        listing.save()
        return Response({'status': listing.status})


@extend_schema(tags=['Wishlist'])
class WishlistView(generics.ListCreateAPIView):
    """Get or add to tenant's wishlist."""
    serializer_class = WishlistSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Wishlist.objects.filter(tenant=self.request.user).select_related('listing')

    def perform_create(self, serializer):
        serializer.save(tenant=self.request.user)


@extend_schema(tags=['Wishlist'])
class WishlistDetailView(generics.DestroyAPIView):
    """Remove a PG from wishlist."""
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Wishlist.objects.filter(tenant=self.request.user)
