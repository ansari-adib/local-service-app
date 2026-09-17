from django.urls import path
from . import views

urlpatterns = [
    # Customer URLs
    path('book/<int:service_pk>/', views.create_booking, name='create_booking'),
    path('my-bookings/', views.my_bookings, name='my_bookings'),
    path('<int:pk>/', views.booking_detail, name='booking_detail'),
    path('<int:pk>/cancel/', views.cancel_booking, name='cancel_booking'),

    # Provider URLs
    path('provider/bookings/', views.provider_bookings, name='provider_bookings'),
    path('<int:pk>/accept/', views.accept_booking, name='accept_booking'),
    path('<int:pk>/reject/', views.reject_booking, name='reject_booking'),
    path('<int:pk>/complete/', views.complete_booking, name='complete_booking'),
]