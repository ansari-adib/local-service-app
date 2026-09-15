from django.db import models


class Notification(models.Model):

    TYPE_BOOKING = 'booking'
    TYPE_REVIEW = 'review'
    TYPE_COMPLAINT = 'complaint'
    TYPE_SYSTEM = 'system'

    TYPE_CHOICES = [
        (TYPE_BOOKING, 'Booking'),
        (TYPE_REVIEW, 'Review'),
        (TYPE_COMPLAINT, 'Complaint'),
        (TYPE_SYSTEM, 'System'),
    ]

    user = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    notification_type = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES,
        default=TYPE_SYSTEM
    )
    title = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Notification for {self.user.username} — {self.title}"
    


# from django.db import models
# from accounts.models import User


# class Notification(models.Model):
#     """
#     In-app notification for a user.
#     Created automatically when important events happen.
#     """

#     TYPE_BOOKING = 'booking'
#     TYPE_REVIEW = 'review'
#     TYPE_COMPLAINT = 'complaint'
#     TYPE_SYSTEM = 'system'

#     TYPE_CHOICES = [
#         (TYPE_BOOKING, 'Booking'),
#         (TYPE_REVIEW, 'Review'),
#         (TYPE_COMPLAINT, 'Complaint'),
#         (TYPE_SYSTEM, 'System'),
#     ]

#     user = models.ForeignKey(
#         User,
#         on_delete=models.CASCADE,
#         related_name='notifications'
#     )
#     notification_type = models.CharField(
#         max_length=20,
#         choices=TYPE_CHOICES,
#         default=TYPE_SYSTEM
#     )
#     title = models.CharField(max_length=200)
#     message = models.TextField()
#     is_read = models.BooleanField(default=False)
#     created_at = models.DateTimeField(auto_now_add=True)

#     class Meta:
#         ordering = ['-created_at']

#     def __str__(self):
#         return f"Notification for {self.user.username} — {self.title}"