from django.db import models
from django.conf import settings


class Notification(models.Model):
    class NotifType(models.TextChoices):
        INQUIRY = 'inquiry', 'New Inquiry'
        INQUIRY_STATUS = 'inquiry_status', 'Inquiry Status Updated'
        KYC_STATUS = 'kyc_status', 'KYC Verification Status'
        LISTING_VIEW_SPIKE = 'view_spike', 'Listing View Spike'
        SYSTEM = 'system', 'System Notification'

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    notif_type = models.CharField(max_length=20, choices=NotifType.choices)
    title = models.CharField(max_length=255)
    body = models.TextField()
    is_read = models.BooleanField(default=False)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.notif_type} → {self.user.full_name}'
