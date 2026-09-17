 
from .models import Notification


def send_notification(user, title, message, notification_type='booking'):
    """
    Creates an in-app notification for a user.
    Call this whenever an important event happens.
    """
    Notification.objects.create(
        user=user,
        title=title,
        message=message,
        notification_type=notification_type
    )


def notify_booking_received(booking):
    """Provider receives notification when new booking arrives."""
    send_notification(
        user=booking.service.provider.user,
        title='New Booking Request',
        message=f'{booking.customer.get_full_name() or booking.customer.username} '
                f'has requested your service "{booking.service.name}" '
                f'on {booking.booking_date}.',
        notification_type='booking'
    )


def notify_booking_accepted(booking):
    """Customer receives notification when booking is accepted."""
    send_notification(
        user=booking.customer,
        title='Booking Accepted',
        message=f'Your booking for "{booking.service.name}" on '
                f'{booking.booking_date} has been accepted by the provider.',
        notification_type='booking'
    )


def notify_booking_rejected(booking):
    """Customer receives notification when booking is rejected."""
    send_notification(
        user=booking.customer,
        title='Booking Rejected',
        message=f'Your booking for "{booking.service.name}" on '
                f'{booking.booking_date} was rejected. '
                f'Reason: {booking.rejection_reason}',
        notification_type='booking'
    )


def notify_booking_completed(booking):
    """Customer receives notification when booking is completed."""
    send_notification(
        user=booking.customer,
        title='Service Completed',
        message=f'Your service "{booking.service.name}" has been marked '
                f'as completed. Please leave a review!',
        notification_type='booking'
    )


def notify_booking_cancelled(booking):
    """Provider receives notification when customer cancels."""
    send_notification(
        user=booking.service.provider.user,
        title='Booking Cancelled',
        message=f'The booking for "{booking.service.name}" on '
                f'{booking.booking_date} was cancelled by the customer.',
        notification_type='booking'
    )