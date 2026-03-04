import random
import string
from django.utils import timezone
from datetime import timedelta
from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from drf_spectacular.utils import extend_schema, OpenApiResponse
from django.contrib.auth import get_user_model

from .models import OTPVerification, KYCDocument
from .serializers import (
    UserRegistrationSerializer,
    UserProfileSerializer,
    OTPRequestSerializer,
    OTPVerifySerializer,
    CustomTokenSerializer,
    PasswordChangeSerializer,
    KYCDocumentSerializer,
)

User = get_user_model()


def generate_otp():
    return ''.join(random.choices(string.digits, k=6))


@extend_schema(tags=['Auth'])
class RegisterView(generics.CreateAPIView):
    """Register a new user (tenant or owner). Returns JWT tokens on success."""
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': UserProfileSerializer(user).data,
        }, status=status.HTTP_201_CREATED)


@extend_schema(tags=['Auth'])
class LoginView(APIView):
    """Obtain JWT access + refresh tokens via email/password."""
    permission_classes = [permissions.AllowAny]
    serializer_class = CustomTokenSerializer

    def post(self, request):
        serializer = CustomTokenSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data)


@extend_schema(tags=['Auth'])
class LogoutView(APIView):
    """Blacklist the refresh token to logout."""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data['refresh']
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({'detail': 'Successfully logged out.'})
        except Exception:
            return Response({'detail': 'Invalid token.'}, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(tags=['Auth'])
class OTPRequestView(APIView):
    """Send OTP to phone number via MSG91/Twilio."""
    permission_classes = [permissions.AllowAny]
    serializer_class = OTPRequestSerializer

    def post(self, request):
        serializer = OTPRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone = serializer.validated_data['phone']

        otp = generate_otp()
        expires_at = timezone.now() + timedelta(minutes=10)

        OTPVerification.objects.create(phone=phone, otp=otp, expires_at=expires_at)

        # TODO: Integrate MSG91/Twilio to send SMS
        # send_sms(phone, f'Your PG Finder OTP is {otp}. Valid for 10 minutes.')

        return Response({'detail': f'OTP sent to {phone}. Valid for 10 minutes.'})


@extend_schema(tags=['Auth'])
class OTPVerifyView(APIView):
    """Verify OTP and mark phone as verified. Returns JWT tokens if user exists."""
    permission_classes = [permissions.AllowAny]
    serializer_class = OTPVerifySerializer

    def post(self, request):
        serializer = OTPVerifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        record = serializer.validated_data['record']
        record.is_used = True
        record.save()

        phone = serializer.validated_data['phone']
        try:
            user = User.objects.get(phone=phone)
            user.is_phone_verified = True
            user.save()
            refresh = RefreshToken.for_user(user)
            return Response({
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'user': UserProfileSerializer(user).data,
            })
        except User.DoesNotExist:
            return Response({'detail': 'Phone verified. Proceed to registration.'})


@extend_schema(tags=['Auth'])
class TokenRefreshView(TokenRefreshView):
    """Refresh access token using refresh token."""
    pass


@extend_schema(tags=['Profile'])
class ProfileView(generics.RetrieveUpdateAPIView):
    """Get or update the authenticated user's profile."""
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


@extend_schema(tags=['Profile'])
class PasswordChangeView(APIView):
    """Change password for authenticated user."""
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = PasswordChangeSerializer

    def post(self, request):
        serializer = PasswordChangeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user
        if not user.check_password(serializer.validated_data['old_password']):
            return Response({'old_password': 'Incorrect password.'}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(serializer.validated_data['new_password'])
        user.save()
        return Response({'detail': 'Password changed successfully.'})


@extend_schema(tags=['Profile'])
class KYCUploadView(generics.ListCreateAPIView):
    """Upload KYC documents (Aadhaar, Property proof, Student/Company ID)."""
    serializer_class = KYCDocumentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return KYCDocument.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
