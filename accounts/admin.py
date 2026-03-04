from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, OTPVerification, KYCDocument


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['email', 'full_name', 'user_type', 'is_phone_verified', 'is_kyc_verified', 'date_joined']
    list_filter = ['user_type', 'is_phone_verified', 'is_kyc_verified', 'is_active']
    search_fields = ['email', 'full_name', 'phone']
    ordering = ['-date_joined']
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('full_name', 'phone', 'profile_photo', 'user_type')}),
        ('Verification', {'fields': ('is_phone_verified', 'is_email_verified', 'is_kyc_verified')}),
        ('Tenant Info', {'fields': (
            'student_college', 'student_course', 'student_year',
            'company_name', 'designation', 'office_location',
            'move_in_date', 'budget_min', 'budget_max',
            'preferred_city', 'preferred_locality', 'gender_preference', 'meal_preference',
        )}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
    )
    add_fieldsets = (
        (None, {'classes': ('wide',), 'fields': ('email', 'full_name', 'user_type', 'password1', 'password2')}),
    )


@admin.register(OTPVerification)
class OTPVerificationAdmin(admin.ModelAdmin):
    list_display = ['phone', 'otp', 'is_used', 'created_at', 'expires_at']
    list_filter = ['is_used']


@admin.register(KYCDocument)
class KYCDocumentAdmin(admin.ModelAdmin):
    list_display = ['user', 'doc_type', 'is_verified', 'uploaded_at']
    list_filter = ['doc_type', 'is_verified']
    actions = ['approve_documents']

    @admin.action(description='Approve selected KYC documents')
    def approve_documents(self, request, queryset):
        from django.utils import timezone
        queryset.update(is_verified=True, verified_at=timezone.now())
