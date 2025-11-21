from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib.auth.models import BaseUserManager
class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")
        
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)
class CustomUser(AbstractUser):
    username = None  # Remove default username field

    fullname = models.CharField(max_length=255, blank=True)
    email = models.EmailField(unique=True)

    company = models.ForeignKey(
        'attendance.companyProfile',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    site = models.ForeignKey(
        'sitevisit.siteProfile',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []  # No username required

    objects = CustomUserManager()  # <-- IMPORTANT

    def __str__(self):
        return self.email



class PasswordResetOTP(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    otp = models.CharField(max_length=6)
    expires_at = models.DateTimeField()
    used = models.BooleanField(default=False)

    def is_valid(self):
        """Check if the OTP is still valid (not used and not expired)."""
        return not self.used and timezone.now() < self.expires_at

    def __str__(self):
        return f"{self.user.email} - {self.otp}"
    
