from django.urls import path
from . import views

urlpatterns = [
    # Public URLs
    path('', views.service_list, name='service_list'),
    path('<int:pk>/', views.service_detail, name='service_detail'),
    path('category/<int:pk>/', views.category_services, name='category_services'),
    path('provider/<int:pk>/', views.provider_public_profile, name='provider_public_profile'),

    # Provider URLs
    path('my-services/', views.my_services, name='my_services'),
    path('add/', views.add_service, name='add_service'),
    path('edit/<int:pk>/', views.edit_service, name='edit_service'),
    path('delete/<int:pk>/', views.delete_service, name='delete_service'),
]