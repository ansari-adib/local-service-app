from django.db import models


class Complaint(models.Model):
    ...
    submitted_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='complaints_submitted'
    )
    booking = models.ForeignKey(
        'bookings.Booking',
        on_delete=models.CASCADE,
        related_name='complaints',
        null=True,
        blank=True
    )


# from django.db import models
# from accounts.models import User
# from bookings.models import Booking


# class Complaint(models.Model):
#     """
#     A complaint submitted by customer or provider
#     about a booking. Managed by admin.
#     """

#     STATUS_OPEN = 'open'
#     STATUS_UNDER_REVIEW = 'under_review'
#     STATUS_RESOLVED = 'resolved'
#     STATUS_CLOSED = 'closed'

#     STATUS_CHOICES = [
#         (STATUS_OPEN, 'Open'),
#         (STATUS_UNDER_REVIEW, 'Under Review'),
#         (STATUS_RESOLVED, 'Resolved'),
#         (STATUS_CLOSED, 'Closed'),
#     ]

#     submitted_by = models.ForeignKey(
#         User,
#         on_delete=models.CASCADE,
#         related_name='complaints_submitted'
#     )
#     booking = models.ForeignKey(
#         Booking,
#         on_delete=models.CASCADE,
#         related_name='complaints',
#         null=True,
#         blank=True
#     )
#     subject = models.CharField(max_length=200)
#     description = models.TextField()
#     status = models.CharField(
#         max_length=20,
#         choices=STATUS_CHOICES,
#         default=STATUS_OPEN
#     )
#     admin_response = models.TextField(blank=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     class Meta:
#         ordering = ['-created_at']

#     def __str__(self):
#         return f"Complaint #{self.id} — {self.subject} ({self.status})"