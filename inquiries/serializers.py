from rest_framework import serializers
from .models import Inquiry
from accounts.serializers import PublicUserSerializer
from listings.serializers import ListingListSerializer


class InquirySerializer(serializers.ModelSerializer):
    tenant = PublicUserSerializer(read_only=True)
    listing = ListingListSerializer(read_only=True)
    listing_id = serializers.PrimaryKeyRelatedField(
        queryset=__import__('listings.models', fromlist=['Listing']).Listing.objects.filter(status='active'),
        source='listing',
        write_only=True,
    )

    class Meta:
        model = Inquiry
        fields = ['id', 'tenant', 'listing', 'listing_id', 'message', 'status', 'move_in_date', 'created_at', 'updated_at']
        read_only_fields = ['id', 'tenant', 'status', 'created_at', 'updated_at']


class InquiryStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Inquiry
        fields = ['status']
