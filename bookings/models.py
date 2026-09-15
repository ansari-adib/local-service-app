from django.db import models


class Booking(models.Model):

    STATUS_PENDING = 'pending'
    STATUS_ACCEPTED = 'accepted'
    STATUS_REJECTED = 'rejected'
    STATUS_IN_PROGRESS = 'in_progress'
    STATUS_COMPLETED = 'completed'
    STATUS_CANCELLED = 'cancelled'

    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_ACCEPTED, 'Accepted'),
        (STATUS_REJECTED, 'Rejected'),
        (STATUS_IN_PROGRESS, 'In Progress'),
        (STATUS_COMPLETED, 'Completed'),
        (STATUS_CANCELLED, 'Cancelled'),
    ]

    SLOT_MORNING = 'morning'
    SLOT_AFTERNOON = 'afternoon'
    SLOT_EVENING = 'evening'

    SLOT_CHOICES = [
        (SLOT_MORNING, 'Morning (8AM - 12PM)'),
        (SLOT_AFTERNOON, 'Afternoon (12PM - 4PM)'),
        (SLOT_EVENING, 'Evening (4PM - 8PM)'),
    ]

    customer = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='bookings_as_customer'
    )
    service = models.ForeignKey(
        'services.Service',
        on_delete=models.CASCADE,
        related_name='bookings'
    )
    booking_date = models.DateField()
    time_slot = models.CharField(
        max_length=20,
        choices=SLOT_CHOICES,
        default=SLOT_MORNING
    )
    address = models.TextField()
    city = models.CharField(max_length=100)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING
    )
    notes = models.TextField(blank=True)
    rejection_reason = models.TextField(blank=True)
    total_price = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Booking #{self.id} — {self.customer.username} → {self.service.name}"

    def can_be_cancelled_by_customer(self):
        return self.status in [self.STATUS_PENDING, self.STATUS_ACCEPTED]

    def can_be_accepted_by_provider(self):
        return self.status == self.STATUS_PENDING

    def can_be_completed_by_provider(self):
        return self.status in [self.STATUS_ACCEPTED, self.STATUS_IN_PROGRESS]


# from django.db import models
# from accounts.models import User
# from django.db import models
# from accounts.models import User


# #class Booking(models.Model):


# class Booking(models.Model):
#     """
#     Complete booking record between a customer and a service.
#     Tracks the full lifecycle from pending to completed.
#     """

#     # Booking Status Choices
#     STATUS_PENDING = 'pending'
#     STATUS_ACCEPTED = 'accepted'
#     STATUS_REJECTED = 'rejected'
#     STATUS_IN_PROGRESS = 'in_progress'
#     STATUS_COMPLETED = 'completed'
#     STATUS_CANCELLED = 'cancelled'

#     STATUS_CHOICES = [
#         (STATUS_PENDING, 'Pending'),
#         (STATUS_ACCEPTED, 'Accepted'),
#         (STATUS_REJECTED, 'Rejected'),
#         (STATUS_IN_PROGRESS, 'In Progress'),
#         (STATUS_COMPLETED, 'Completed'),
#         (STATUS_CANCELLED, 'Cancelled'),
#     ]

#     # Time Slot Choices
#     SLOT_MORNING = 'morning'
#     SLOT_AFTERNOON = 'afternoon'
#     SLOT_EVENING = 'evening'

#     SLOT_CHOICES = [
#         (SLOT_MORNING, 'Morning (8AM - 12PM)'),
#         (SLOT_AFTERNOON, 'Afternoon (12PM - 4PM)'),
#         (SLOT_EVENING, 'Evening (4PM - 8PM)'),
#     ]

#     customer = models.ForeignKey(
#         User,
#         on_delete=models.CASCADE,
#         related_name='bookings_as_customer'
#     )
#     service = models.ForeignKey(
#     'services.Service',
#     on_delete=models.CASCADE,
#     related_name='bookings'
# )
#     booking_date = models.DateField()
#     time_slot = models.CharField(
#         max_length=20,
#         choices=SLOT_CHOICES,
#         default=SLOT_MORNING
#     )
#     address = models.TextField(
#         help_text='Address where service is needed'
#     )
#     city = models.CharField(max_length=100)
#     status = models.CharField(
#         max_length=20,
#         choices=STATUS_CHOICES,
#         default=STATUS_PENDING
#     )
#     notes = models.TextField(
#         blank=True,
#         help_text='Any special instructions from the customer'
#     )
#     rejection_reason = models.TextField(blank=True)
#     total_price = models.DecimalField(
#         max_digits=8,
#         decimal_places=2,
#         null=True,
#         blank=True
#     )
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     class Meta:
#         ordering = ['-created_at']

#     def __str__(self):
#         return f"Booking #{self.id} — {self.customer.username} → {self.service.name}"

#     def can_be_cancelled_by_customer(self):
#         """Customer can only cancel pending or accepted bookings."""
#         return self.status in [self.STATUS_PENDING, self.STATUS_ACCEPTED]

#     def can_be_accepted_by_provider(self):
#         """Provider can only accept pending bookings."""
#         return self.status == self.STATUS_PENDING

#     def can_be_completed_by_provider(self):
#         """Provider can only mark accepted or in_progress as completed."""
#         return self.status in [self.STATUS_ACCEPTED, self.STATUS_IN_PROGRESS]