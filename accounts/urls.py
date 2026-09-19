from django.urls import path
from . import views

urlpatterns = [
    # Public
    path('', views.home, name='home'),

    # Auth
    path('accounts/register/customer/', views.register_customer, name='register_customer'),
    path('accounts/register/provider/', views.register_provider, name='register_provider'),
    path('accounts/login/', views.user_login, name='login'),
    path('accounts/logout/', views.user_logout, name='logout'),

    # Dashboards
    path('accounts/dashboard/', views.dashboard, name='dashboard'),
    path('accounts/customer/dashboard/', views.customer_dashboard, name='customer_dashboard'),
    path('accounts/provider/dashboard/', views.provider_dashboard, name='provider_dashboard'),
    path('accounts/admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),

    # Profile
    path('accounts/profile/update/', views.update_profile, name='update_profile'),

    # Admin Management
    path('accounts/admin/users/', views.admin_users, name='admin_users'),
    path('accounts/admin/users/<int:pk>/toggle/', views.admin_toggle_user, name='admin_toggle_user'),
    path('accounts/admin/providers/<int:pk>/verify/', views.admin_verify_provider, name='admin_verify_provider'),
    path('accounts/admin/bookings/', views.admin_all_bookings, name='admin_all_bookings'),
    path('accounts/admin/services/', views.admin_all_services, name='admin_all_services'),
]