from django.db import models
from django.conf import settings
from listings.models import Listing


class Inquiry(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        RESPONDED = 'responded', 'Responded'
        ACCEPTED = 'accepted', 'Accepted'
        REJECTED = 'rejected', 'Rejected'
        CLOSED = 'closed', 'Closed'

    tenant = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_inquiries'
    )
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='inquiries')
    message = models.TextField()
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.PENDING)
    move_in_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ['tenant', 'listing']

    def __str__(self):
        return f'Inquiry from {self.tenant.full_name} → {self.listing.name}'
