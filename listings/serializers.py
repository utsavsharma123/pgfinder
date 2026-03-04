from rest_framework import serializers
from .models import Listing, ListingPhoto, Wishlist
from accounts.serializers import PublicUserSerializer


class ListingPhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ListingPhoto
        fields = ['id', 'url', 'caption', 'order']


class ListingListSerializer(serializers.ModelSerializer):
    """Compact serializer for list/search views."""
    cover_photo = serializers.SerializerMethodField()
    owner_name = serializers.CharField(source='owner.full_name', read_only=True)
    owner_verified = serializers.BooleanField(source='owner.is_kyc_verified', read_only=True)
    min_price = serializers.SerializerMethodField()

    class Meta:
        model = Listing
        fields = [
            'id', 'name', 'city', 'locality', 'address',
            'gender_type', 'meal_option', 'status',
            'price_single', 'price_double', 'price_triple', 'min_price',
            'total_beds', 'vacant_beds',
            'has_wifi', 'has_ac', 'has_geyser', 'has_washing_machine',
            'has_cctv', 'has_power_backup', 'is_featured',
            'total_views', 'total_inquiries',
            'latitude', 'longitude',
            'cover_photo', 'owner_name', 'owner_verified',
            'created_at',
        ]

    def get_cover_photo(self, obj):
        photo = obj.photos.first()
        return photo.url if photo else None

    def get_min_price(self, obj):
        prices = [p for p in [obj.price_single, obj.price_double, obj.price_triple] if p]
        return min(prices) if prices else None


class ListingDetailSerializer(serializers.ModelSerializer):
    """Full serializer for detail view."""
    photos = ListingPhotoSerializer(many=True, read_only=True)
    owner = PublicUserSerializer(read_only=True)
    min_price = serializers.SerializerMethodField()

    class Meta:
        model = Listing
        fields = [
            'id', 'name', 'description', 'status',
            'city', 'locality', 'address', 'pincode',
            'latitude', 'longitude', 'google_maps_url',
            'gender_type', 'meal_option',
            'price_single', 'price_double', 'price_triple', 'min_price',
            'deposit_amount', 'lock_in_months',
            'total_beds', 'vacant_beds',
            # Amenities
            'has_wifi', 'has_ac', 'has_geyser', 'has_washing_machine',
            'has_cctv', 'has_power_backup', 'has_parking', 'has_lift',
            'has_gym', 'has_housekeeping',
            # Rules
            'rule_no_smoking', 'rule_no_alcohol',
            'curfew_time', 'guest_policy', 'pet_policy',
            'is_featured', 'total_views', 'total_inquiries',
            'photos', 'owner',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'owner', 'total_views', 'total_inquiries', 'created_at', 'updated_at']

    def get_min_price(self, obj):
        prices = [p for p in [obj.price_single, obj.price_double, obj.price_triple] if p]
        return min(prices) if prices else None


class ListingCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Listing
        exclude = ['owner', 'total_views', 'total_inquiries', 'is_featured', 'created_at', 'updated_at']

    def validate_vacant_beds(self, value):
        total = self.initial_data.get('total_beds', 0)
        if value > int(total):
            raise serializers.ValidationError('Vacant beds cannot exceed total beds.')
        return value


class WishlistSerializer(serializers.ModelSerializer):
    listing = ListingListSerializer(read_only=True)
    listing_id = serializers.PrimaryKeyRelatedField(
        queryset=Listing.objects.filter(status='active'),
        source='listing',
        write_only=True,
    )

    class Meta:
        model = Wishlist
        fields = ['id', 'listing', 'listing_id', 'added_at']
        read_only_fields = ['id', 'added_at']
