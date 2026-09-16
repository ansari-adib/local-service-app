from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('accounts/register/customer/', views.register_customer, name='register_customer'),
    path('accounts/register/provider/', views.register_provider, name='register_provider'),
    path('accounts/login/', views.user_login, name='login'),
    path('accounts/logout/', views.user_logout, name='logout'),
    path('accounts/dashboard/', views.dashboard, name='dashboard'),
    path('accounts/customer/dashboard/', views.customer_dashboard, name='customer_dashboard'),
    path('accounts/provider/dashboard/', views.provider_dashboard, name='provider_dashboard'),
    path('accounts/admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('accounts/profile/update/', views.update_profile, name='update_profile'),
]