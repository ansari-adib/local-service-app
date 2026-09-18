from django.urls import path
from . import views

urlpatterns = [
    path('add/<int:booking_pk>/', views.add_review, name='add_review'),
    path('my-reviews/', views.my_reviews, name='my_reviews'),
    path('provider-reviews/', views.provider_reviews, name='provider_reviews'),
]