import uuid
import boto3
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from drf_spectacular.utils import extend_schema
from django.conf import settings


@extend_schema(tags=['Media'])
class PresignedUploadView(APIView):
    """
    Generate an S3 presigned URL for direct client-side photo upload.
    Returns a URL + fields the client uses to POST the file directly to S3.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        file_type = request.data.get('file_type', 'image/jpeg')
        folder = request.data.get('folder', 'listings')

        if not settings.USE_S3:
            return Response({
                'message': 'S3 not configured. Set USE_S3=True and AWS credentials.',
                'upload_url': None,
            })

        allowed_types = ['image/jpeg', 'image/png', 'image/webp', 'application/pdf']
        if file_type not in allowed_types:
            return Response({'detail': 'File type not allowed.'}, status=status.HTTP_400_BAD_REQUEST)

        ext = file_type.split('/')[-1]
        key = f'{folder}/{request.user.id}/{uuid.uuid4()}.{ext}'

        s3 = boto3.client(
            's3',
            region_name=settings.AWS_S3_REGION_NAME,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        )

        presigned = s3.generate_presigned_post(
            Bucket=settings.AWS_STORAGE_BUCKET_NAME,
            Key=key,
            Fields={'Content-Type': file_type},
            Conditions=[{'Content-Type': file_type}, ['content-length-range', 1, 10 * 1024 * 1024]],  # max 10MB
            ExpiresIn=300,
        )

        cdn_base = f'https://{settings.AWS_S3_CUSTOM_DOMAIN}' if settings.AWS_S3_CUSTOM_DOMAIN else f'https://{settings.AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'
        file_url = f'{cdn_base}/{key}'

        return Response({
            'upload_url': presigned['url'],
            'fields': presigned['fields'],
            'file_url': file_url,
            'key': key,
        })
