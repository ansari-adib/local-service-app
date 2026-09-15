from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, CustomerProfile, ProviderProfile


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ['username', 'email', 'role', 'phone', 'is_active']
    list_filter = ['role', 'is_active']
    fieldsets = UserAdmin.fieldsets + (
        ('Role & Contact', {'fields': ('role', 'phone')}),
    )


@admin.register(CustomerProfile)
class CustomerProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'city', 'created_at']
    search_fields = ['user__username']


@admin.register(ProviderProfile)
class ProviderProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'city', 'is_verified', 'is_available', 'average_rating']
    list_filter = ['is_verified', 'is_available']
    search_fields = ['user__username']


# from django.contrib import admin
# from django.contrib.auth.admin import UserAdmin
# from .models import User


# @admin.register(User)
# class CustomUserAdmin(UserAdmin):
#     list_display = ['username', 'email', 'role', 'phone', 'is_active']
#     list_filter = ['role', 'is_active']
#     fieldsets = UserAdmin.fieldsets + (
#         ('Role & Contact', {'fields': ('role', 'phone')}),
#     )