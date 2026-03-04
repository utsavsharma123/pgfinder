from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email is required')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('user_type', User.UserType.ADMIN)
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    class UserType(models.TextChoices):
        TENANT = 'tenant', 'Tenant'
        OWNER = 'owner', 'PG Owner'
        ADMIN = 'admin', 'Admin'

    class GenderPreference(models.TextChoices):
        MALE = 'male', 'Male'
        FEMALE = 'female', 'Female'
        ANY = 'any', 'Any'

    class MealPreference(models.TextChoices):
        NO_MEALS = 'no_meals', 'No Meals'
        BREAKFAST = 'breakfast', 'Breakfast Only'
        ALL_MEALS = 'all_meals', 'All Meals'

    # Core fields
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15, blank=True)
    full_name = models.CharField(max_length=255)
    user_type = models.CharField(max_length=10, choices=UserType.choices, default=UserType.TENANT)
    profile_photo = models.URLField(blank=True)

    # Flags
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_phone_verified = models.BooleanField(default=False)
    is_email_verified = models.BooleanField(default=False)
    is_kyc_verified = models.BooleanField(default=False)  # For owners

    # Timestamps
    date_joined = models.DateTimeField(default=timezone.now)
    last_seen = models.DateTimeField(auto_now=True)

    # Tenant-specific
    student_college = models.CharField(max_length=255, blank=True)
    student_course = models.CharField(max_length=100, blank=True)
    student_year = models.CharField(max_length=20, blank=True)
    company_name = models.CharField(max_length=255, blank=True)
    designation = models.CharField(max_length=100, blank=True)
    office_location = models.CharField(max_length=255, blank=True)
    move_in_date = models.DateField(null=True, blank=True)
    budget_min = models.PositiveIntegerField(null=True, blank=True)
    budget_max = models.PositiveIntegerField(null=True, blank=True)
    preferred_city = models.CharField(max_length=100, blank=True)
    preferred_locality = models.CharField(max_length=100, blank=True)
    gender_preference = models.CharField(
        max_length=10, choices=GenderPreference.choices, default=GenderPreference.ANY
    )
    meal_preference = models.CharField(
        max_length=10, choices=MealPreference.choices, default=MealPreference.NO_MEALS
    )

    # Owner-specific
    owner_city = models.CharField(max_length=100, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name']
    objects = UserManager()

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-date_joined']

    def __str__(self):
        return f'{self.full_name} ({self.email})'

    @property
    def is_tenant(self):
        return self.user_type == self.UserType.TENANT

    @property
    def is_owner(self):
        return self.user_type == self.UserType.OWNER


class OTPVerification(models.Model):
    phone = models.CharField(max_length=15)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)
    expires_at = models.DateTimeField()

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'OTP for {self.phone}'


class KYCDocument(models.Model):
    class DocType(models.TextChoices):
        AADHAAR = 'aadhaar', 'Aadhaar Card'
        PROPERTY = 'property', 'Property Proof'
        STUDENT_ID = 'student_id', 'Student ID'
        COMPANY_ID = 'company_id', 'Company ID'

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='kyc_documents')
    doc_type = models.CharField(max_length=20, choices=DocType.choices)
    doc_url = models.URLField()
    uploaded_at = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)
    verified_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True)

    class Meta:
        ordering = ['-uploaded_at']

    def __str__(self):
        return f'{self.doc_type} for {self.user.full_name}'
