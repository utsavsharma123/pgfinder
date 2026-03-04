from celery import shared_task
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


@shared_task
def send_email_notification(to_email, subject, body):
    """Send transactional email via SendGrid."""
    from django.core.mail import send_mail
    try:
        send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, [to_email])
        logger.info(f'Email sent to {to_email}: {subject}')
    except Exception as e:
        logger.error(f'Email failed to {to_email}: {e}')


@shared_task
def send_sms_notification(phone, message):
    """Send SMS via MSG91."""
    import requests
    try:
        resp = requests.post(
            'https://api.msg91.com/api/v5/flow/',
            json={
                'template_id': settings.MSG91_TEMPLATE_ID,
                'recipients': [{'mobiles': phone, 'var1': message}],
            },
            headers={'authkey': settings.MSG91_AUTH_KEY},
            timeout=10,
        )
        logger.info(f'SMS sent to {phone}, status: {resp.status_code}')
    except Exception as e:
        logger.error(f'SMS failed to {phone}: {e}')


@shared_task
def notify_owner_new_inquiry(inquiry_id):
    """Notify owner when a new inquiry is received."""
    from inquiries.models import Inquiry
    from .models import Notification
    try:
        inquiry = Inquiry.objects.select_related('tenant', 'listing__owner').get(pk=inquiry_id)
        owner = inquiry.listing.owner
        Notification.objects.create(
            user=owner,
            notif_type='inquiry',
            title='New Inquiry Received',
            body=f'{inquiry.tenant.full_name} sent an inquiry for {inquiry.listing.name}.',
            metadata={'inquiry_id': inquiry_id, 'listing_id': inquiry.listing.id},
        )
        send_email_notification.delay(
            owner.email,
            f'New Inquiry for {inquiry.listing.name}',
            f'{inquiry.tenant.full_name} is interested in your PG. Log in to respond.',
        )
    except Exception as e:
        logger.error(f'Failed to notify owner for inquiry {inquiry_id}: {e}')
