from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):

    ROLE_CUSTOMER = 'customer'
    ROLE_PROVIDER = 'provider'
    ROLE_ADMIN = 'admin'

    ROLE_CHOICES = [
        (ROLE_CUSTOMER, 'Customer'),
        (ROLE_PROVIDER, 'Service Provider'),
        (ROLE_ADMIN, 'Administrator'),
    ]

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default=ROLE_CUSTOMER,
    )

    phone = models.CharField(max_length=15, blank=True)
    email = models.EmailField(unique=True)

    def is_customer(self):
        return self.role == self.ROLE_CUSTOMER

    def is_provider(self):
        return self.role == self.ROLE_PROVIDER

    def is_admin_user(self):
        return self.role == self.ROLE_ADMIN

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"


class CustomerProfile(models.Model):

    user = models.OneToOneField(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='customer_profile'
    )
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    profile_photo = models.ImageField(
        upload_to='customer_photos/',
        blank=True,
        null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Customer Profile — {self.user.username}"


class ProviderProfile(models.Model):

    user = models.OneToOneField(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='provider_profile'
    )
    bio = models.TextField(blank=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    experience_years = models.PositiveIntegerField(default=0)
    profile_photo = models.ImageField(
        upload_to='provider_photos/',
        blank=True,
        null=True
    )
    is_verified = models.BooleanField(default=False)
    is_available = models.BooleanField(default=True)
    average_rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=0.00
    )
    total_reviews = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Provider Profile — {self.user.username}"



# from django.contrib.auth.models import AbstractUser
# from django.db import models


# class User(AbstractUser):
    
#     ROLE_CUSTOMER = 'customer'
#     ROLE_PROVIDER = 'provider'
#     ROLE_ADMIN = 'admin'
    
#     ROLE_CHOICES = [
#         (ROLE_CUSTOMER, 'Customer'),
#         (ROLE_PROVIDER, 'Service Provider'),
#         (ROLE_ADMIN, 'Administrator'),
#     ]
    
#     role = models.CharField(
#         max_length=20,
#         choices=ROLE_CHOICES,
#         default=ROLE_CUSTOMER,
#     )
    
#     phone = models.CharField(max_length=15, blank=True)
    
#     def is_customer(self):
#         return self.role == self.ROLE_CUSTOMER
    
#     def is_provider(self):
#         return self.role == self.ROLE_PROVIDER
    
#     def is_admin(self):
#         return self.role == self.ROLE_ADMIN
    
#     def __str__(self):
#         return f"{self.username} ({self.role})"