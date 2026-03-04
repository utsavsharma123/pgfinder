from django.db import models
from django.conf import settings


class Listing(models.Model):
    class Status(models.TextChoices):
        DRAFT = 'draft', 'Draft'
        ACTIVE = 'active', 'Active'
        OCCUPIED = 'occupied', 'Occupied'
        SUSPENDED = 'suspended', 'Suspended'

    class GenderType(models.TextChoices):
        MALE = 'male', 'Men Only'
        FEMALE = 'female', 'Women Only'
        COED = 'coed', 'Co-ed'

    class MealOption(models.TextChoices):
        NO_MEALS = 'no_meals', 'No Meals'
        BREAKFAST = 'breakfast', 'Breakfast Only'
        ALL_MEALS = 'all_meals', 'All Meals'

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='listings',
        limit_choices_to={'user_type': 'owner'},
    )

    # Basic info
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.DRAFT)
    gender_type = models.CharField(max_length=10, choices=GenderType.choices)
    meal_option = models.CharField(max_length=10, choices=MealOption.choices, default=MealOption.NO_MEALS)

    # Location
    address = models.TextField()
    city = models.CharField(max_length=100, db_index=True)
    locality = models.CharField(max_length=100, db_index=True)
    pincode = models.CharField(max_length=10, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    google_maps_url = models.URLField(blank=True)

    # Pricing
    price_single = models.PositiveIntegerField(null=True, blank=True, help_text='Price per bed/month for single room')
    price_double = models.PositiveIntegerField(null=True, blank=True)
    price_triple = models.PositiveIntegerField(null=True, blank=True)
    deposit_amount = models.PositiveIntegerField(default=0)
    lock_in_months = models.PositiveSmallIntegerField(default=1)

    # Capacity
    total_beds = models.PositiveSmallIntegerField(default=0)
    vacant_beds = models.PositiveSmallIntegerField(default=0)

    # Amenities (boolean flags)
    has_wifi = models.BooleanField(default=False)
    has_ac = models.BooleanField(default=False)
    has_geyser = models.BooleanField(default=False)
    has_washing_machine = models.BooleanField(default=False)
    has_cctv = models.BooleanField(default=False)
    has_power_backup = models.BooleanField(default=False)
    has_parking = models.BooleanField(default=False)
    has_lift = models.BooleanField(default=False)
    has_gym = models.BooleanField(default=False)
    has_housekeeping = models.BooleanField(default=False)

    # House rules
    rule_no_smoking = models.BooleanField(default=False)
    rule_no_alcohol = models.BooleanField(default=False)
    curfew_time = models.TimeField(null=True, blank=True)
    guest_policy = models.CharField(max_length=255, blank=True)
    pet_policy = models.CharField(max_length=255, blank=True)

    # Meta
    is_featured = models.BooleanField(default=False)
    total_views = models.PositiveIntegerField(default=0)
    total_inquiries = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['city', 'locality']),
            models.Index(fields=['status', 'gender_type']),
            models.Index(fields=['price_single']),
        ]

    def __str__(self):
        return f'{self.name} — {self.city}'


class ListingPhoto(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='photos')
    url = models.URLField()
    caption = models.CharField(max_length=255, blank=True)
    order = models.PositiveSmallIntegerField(default=0)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', 'uploaded_at']

    def __str__(self):
        return f'Photo for {self.listing.name}'


class Wishlist(models.Model):
    tenant = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='wishlist',
    )
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='wishlisted_by')
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['tenant', 'listing']
        ordering = ['-added_at']

    def __str__(self):
        return f'{self.tenant.full_name} ♥ {self.listing.name}'
