from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
# from accounts.models import User
# from bookings.models import Booking


class Review(models.Model):
    """
    A customer review for a completed booking.
    One booking can have only one review.
    """
    
    booking = models.OneToOneField(
    'bookings.Booking',
    on_delete=models.CASCADE,
    related_name='review'
    )
    customer = models.ForeignKey(
    'accounts.User',
    on_delete=models.CASCADE,
    related_name='reviews_given'
    )
    # booking = models.OneToOneField(
    #     Booking,
    #     on_delete=models.CASCADE,
    #     related_name='review'
    # )
    # customer = models.ForeignKey(
    #     User,
    #     on_delete=models.CASCADE,
    #     related_name='reviews_given'
    # )
    rating = models.PositiveIntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(5)
        ],
        help_text='Rating from 1 to 5'
    )
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Review by {self.customer.username} — {self.rating}/5 stars"