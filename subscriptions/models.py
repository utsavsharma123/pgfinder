from django.db import models
from django.conf import settings


class SubscriptionPlan(models.Model):
    class PlanTier(models.TextChoices):
        FREE = 'free', 'Free'
        STARTER = 'starter', 'Starter'
        PRO = 'pro', 'Pro'
        ENTERPRISE = 'enterprise', 'Enterprise'

    tier = models.CharField(max_length=15, choices=PlanTier.choices, unique=True)
    name = models.CharField(max_length=50)
    price_monthly = models.PositiveIntegerField(help_text='Price in INR paise (multiply by 100 for Razorpay)')
    max_listings = models.PositiveSmallIntegerField(null=True, blank=True, help_text='null = unlimited')
    max_photos_per_listing = models.PositiveSmallIntegerField(default=5)
    has_priority_placement = models.BooleanField(default=False)
    has_featured_badge = models.BooleanField(default=False)
    has_advanced_analytics = models.BooleanField(default=False)
    has_chat_support = models.BooleanField(default=False)
    has_api_access = models.BooleanField(default=False)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Subscription(models.Model):
    class SubStatus(models.TextChoices):
        ACTIVE = 'active', 'Active'
        EXPIRED = 'expired', 'Expired'
        CANCELLED = 'cancelled', 'Cancelled'
        TRIAL = 'trial', 'Trial'

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='subscriptions'
    )
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.PROTECT)
    status = models.CharField(max_length=15, choices=SubStatus.choices, default=SubStatus.ACTIVE)
    razorpay_subscription_id = models.CharField(max_length=100, blank=True)
    razorpay_payment_id = models.CharField(max_length=100, blank=True)
    started_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-started_at']

    def __str__(self):
        return f'{self.owner.full_name} → {self.plan.name}'
