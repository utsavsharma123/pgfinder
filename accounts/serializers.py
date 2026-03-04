from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from .models import OTPVerification, KYCDocument

User = get_user_model()


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            'email', 'full_name', 'phone', 'user_type',
            'password', 'password_confirm',
        ]

    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({'password_confirm': 'Passwords do not match.'})
        return data

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id', 'email', 'full_name', 'phone', 'user_type',
            'profile_photo', 'is_phone_verified', 'is_email_verified', 'is_kyc_verified',
            'student_college', 'student_course', 'student_year',
            'company_name', 'designation', 'office_location',
            'move_in_date', 'budget_min', 'budget_max',
            'preferred_city', 'preferred_locality',
            'gender_preference', 'meal_preference', 'owner_city',
            'date_joined', 'last_seen',
        ]
        read_only_fields = [
            'id', 'email', 'user_type', 'is_phone_verified',
            'is_email_verified', 'is_kyc_verified', 'date_joined', 'last_seen',
        ]


class PublicUserSerializer(serializers.ModelSerializer):
    """Minimal user info for public-facing endpoints (e.g., listing owner)."""
    class Meta:
        model = User
        fields = ['id', 'full_name', 'profile_photo', 'is_kyc_verified', 'date_joined']


class OTPRequestSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=15)


class OTPVerifySerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=15)
    otp = serializers.CharField(max_length=6)

    def validate(self, data):
        try:
            record = OTPVerification.objects.filter(
                phone=data['phone'],
                otp=data['otp'],
                is_used=False,
                expires_at__gt=timezone.now(),
            ).latest('created_at')
        except OTPVerification.DoesNotExist:
            raise serializers.ValidationError({'otp': 'Invalid or expired OTP.'})
        data['record'] = record
        return data


class CustomTokenSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['user_type'] = user.user_type
        token['full_name'] = user.full_name
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        data['user'] = UserProfileSerializer(self.user).data
        return data


class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, min_length=8)
    new_password_confirm = serializers.CharField(write_only=True)

    def validate(self, data):
        if data['new_password'] != data['new_password_confirm']:
            raise serializers.ValidationError({'new_password_confirm': 'Passwords do not match.'})
        return data


class KYCDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = KYCDocument
        fields = ['id', 'doc_type', 'doc_url', 'uploaded_at', 'is_verified', 'rejection_reason']
        read_only_fields = ['id', 'uploaded_at', 'is_verified', 'rejection_reason']
