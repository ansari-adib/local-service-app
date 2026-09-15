from django.db import models


class ServiceCategory(models.Model):

    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Service Category'
        verbose_name_plural = 'Service Categories'
        ordering = ['name']

    def __str__(self):
        return self.name


class Service(models.Model):

    provider = models.ForeignKey(
        'accounts.ProviderProfile',
        on_delete=models.CASCADE,
        related_name='services'
    )
    category = models.ForeignKey(
        'services.ServiceCategory',
        on_delete=models.SET_NULL,
        null=True,
        related_name='services'
    )
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=8, decimal_places=2)
    duration_hours = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        default=1.0
    )
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} by {self.provider.user.username}"
# from django.contrib.auth.models import AbstractUser
# from django.db import models


# class User(AbstractUser):
#     """
#     Custom user model for all three roles.
#     Always use this instead of Django's default User.
#     """

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
#     email = models.EmailField(unique=True)

#     def is_customer(self):
#         return self.role == self.ROLE_CUSTOMER

#     def is_provider(self):
#         return self.role == self.ROLE_PROVIDER

#     def is_admin_user(self):
#         return self.role == self.ROLE_ADMIN

#     def __str__(self):
#         return f"{self.username} ({self.get_role_display()})"


# class CustomerProfile(models.Model):
#     """
#     Extra information for customers.
#     One-to-One with User.
#     """

#     user = models.OneToOneField(
#         User,
#         on_delete=models.CASCADE,
#         related_name='customer_profile'
#     )
#     address = models.TextField(blank=True)
#     city = models.CharField(max_length=100, blank=True)
#     profile_photo = models.ImageField(
#         upload_to='customer_photos/',
#         blank=True,
#         null=True
#     )
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     def __str__(self):
#         return f"Customer Profile — {self.user.username}"


# class ProviderProfile(models.Model):
#     """
#     Extra information for service providers.
#     One-to-One with User.
#     """

#     user = models.OneToOneField(
#         User,
#         on_delete=models.CASCADE,
#         related_name='provider_profile'
#     )
#     bio = models.TextField(blank=True)
#     address = models.TextField(blank=True)
#     city = models.CharField(max_length=100, blank=True)
#     experience_years = models.PositiveIntegerField(default=0)
#     profile_photo = models.ImageField(
#         upload_to='provider_photos/',
#         blank=True,
#         null=True
#     )
#     is_verified = models.BooleanField(default=False)
#     is_available = models.BooleanField(default=True)
#     average_rating = models.DecimalField(
#         max_digits=3,
#         decimal_places=2,
#         default=0.00
#     )
#     total_reviews = models.PositiveIntegerField(default=0)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     def __str__(self):
#         return f"Provider Profile — {self.user.username}"