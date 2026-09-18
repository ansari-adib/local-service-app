from django.urls import path
from . import views

urlpatterns = [
    # Customer
    path('submit/', views.submit_complaint, name='submit_complaint'),
    path('submit/<int:booking_pk>/', views.submit_complaint, name='submit_complaint_booking'),
    path('my-complaints/', views.my_complaints, name='my_complaints'),

    # Provider
    path('provider-complaints/', views.provider_complaints, name='provider_complaints'),

    # Shared
    path('<int:pk>/', views.complaint_detail, name='complaint_detail'),

    # Admin
    path('admin/all/', views.admin_complaints, name='admin_complaints'),
    path('admin/<int:pk>/response/', views.admin_complaint_response, name='admin_complaint_response'),
]