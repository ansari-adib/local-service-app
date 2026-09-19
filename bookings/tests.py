from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from datetime import date, timedelta
from accounts.models import User, CustomerProfile, ProviderProfile
from services.models import ServiceCategory, Service
from bookings.models import Booking


class BookingTest(TestCase):
    """Tests for the complete booking workflow."""

    def setUp(self):
        self.client = Client()

        # Create customer
        self.customer = User.objects.create_user(
            username='booking_customer',
            email='bc@test.com',
            password='TestPass@123',
            role=User.ROLE_CUSTOMER
        )
        CustomerProfile.objects.create(user=self.customer)

        # Create provider
        self.provider_user = User.objects.create_user(
            username='booking_provider',
            email='bp@test.com',
            password='TestPass@123',
            role=User.ROLE_PROVIDER
        )
        self.provider_profile = ProviderProfile.objects.create(
            user=self.provider_user,
            city='Delhi',
            experience_years=3
        )

        # Create category and service
        self.category = ServiceCategory.objects.create(
            name='Cleaning',
            is_active=True
        )
        self.service = Service.objects.create(
            provider=self.provider_profile,
            category=self.category,
            name='Home Cleaning',
            description='Complete home cleaning service',
            price=800,
            duration_hours=3,
            is_available=True
        )

        # Future date for booking
        self.future_date = date.today() + timedelta(days=5)

    def test_customer_can_create_booking(self):
        """Customer should be able to create a booking."""
        self.client.login(
            username='booking_customer',
            password='TestPass@123'
        )
        response = self.client.post(
            reverse('create_booking', args=[self.service.pk]),
            {
                'booking_date': self.future_date,
                'time_slot': 'morning',
                'address': '123 Test Street',
                'city': 'Delhi',
                'notes': 'Please bring equipment',
            }
        )
        self.assertEqual(Booking.objects.count(), 1)
        booking = Booking.objects.first()
        self.assertEqual(booking.status, Booking.STATUS_PENDING)
        self.assertEqual(booking.customer, self.customer)

    def test_provider_cannot_book_service(self):
        """Provider should not be able to create a booking."""
        self.client.login(
            username='booking_provider',
            password='TestPass@123'
        )
        response = self.client.post(
            reverse('create_booking', args=[self.service.pk]),
            {
                'booking_date': self.future_date,
                'time_slot': 'morning',
                'address': '123 Test Street',
                'city': 'Delhi',
            }
        )
        self.assertEqual(Booking.objects.count(), 0)

    def test_provider_can_accept_booking(self):
        """Provider should be able to accept a pending booking."""
        booking = Booking.objects.create(
            customer=self.customer,
            service=self.service,
            booking_date=self.future_date,
            time_slot='morning',
            address='123 Test Street',
            city='Delhi',
            status=Booking.STATUS_PENDING,
            total_price=self.service.price
        )
        self.client.login(
            username='booking_provider',
            password='TestPass@123'
        )
        self.client.get(reverse('accept_booking', args=[booking.pk]))
        booking.refresh_from_db()
        self.assertEqual(booking.status, Booking.STATUS_ACCEPTED)

    def test_provider_can_reject_booking(self):
        """Provider should be able to reject a pending booking."""
        booking = Booking.objects.create(
            customer=self.customer,
            service=self.service,
            booking_date=self.future_date,
            time_slot='morning',
            address='123 Test Street',
            city='Delhi',
            status=Booking.STATUS_PENDING,
            total_price=self.service.price
        )
        self.client.login(
            username='booking_provider',
            password='TestPass@123'
        )
        self.client.post(
            reverse('reject_booking', args=[booking.pk]),
            {'rejection_reason': 'Not available on that date'}
        )
        booking.refresh_from_db()
        self.assertEqual(booking.status, Booking.STATUS_REJECTED)

    def test_customer_can_cancel_pending_booking(self):
        """Customer should be able to cancel a pending booking."""
        booking = Booking.objects.create(
            customer=self.customer,
            service=self.service,
            booking_date=self.future_date,
            time_slot='morning',
            address='123 Test Street',
            city='Delhi',
            status=Booking.STATUS_PENDING,
            total_price=self.service.price
        )
        self.client.login(
            username='booking_customer',
            password='TestPass@123'
        )
        self.client.post(
            reverse('cancel_booking', args=[booking.pk])
        )
        booking.refresh_from_db()
        self.assertEqual(booking.status, Booking.STATUS_CANCELLED)

    def test_customer_cannot_cancel_completed_booking(self):
        """Customer should not be able to cancel a completed booking."""
        booking = Booking.objects.create(
            customer=self.customer,
            service=self.service,
            booking_date=self.future_date,
            time_slot='morning',
            address='123 Test Street',
            city='Delhi',
            status=Booking.STATUS_COMPLETED,
            total_price=self.service.price
        )
        self.assertFalse(booking.can_be_cancelled_by_customer())

    def test_provider_can_complete_accepted_booking(self):
        """Provider should be able to mark an accepted booking complete."""
        booking = Booking.objects.create(
            customer=self.customer,
            service=self.service,
            booking_date=self.future_date,
            time_slot='morning',
            address='123 Test Street',
            city='Delhi',
            status=Booking.STATUS_ACCEPTED,
            total_price=self.service.price
        )
        self.client.login(
            username='booking_provider',
            password='TestPass@123'
        )
        self.client.post(
            reverse('complete_booking', args=[booking.pk])
        )
        booking.refresh_from_db()
        self.assertEqual(booking.status, Booking.STATUS_COMPLETED)

    def test_other_customer_cannot_view_booking(self):
        """Another customer should not be able to view someone else's booking."""
        booking = Booking.objects.create(
            customer=self.customer,
            service=self.service,
            booking_date=self.future_date,
            time_slot='morning',
            address='123 Test Street',
            city='Delhi',
            status=Booking.STATUS_PENDING,
            total_price=self.service.price
        )
        other_customer = User.objects.create_user(
            username='other_customer',
            email='other@test.com',
            password='TestPass@123',
            role=User.ROLE_CUSTOMER
        )
        CustomerProfile.objects.create(user=other_customer)
        self.client.login(
            username='other_customer',
            password='TestPass@123'
        )
        response = self.client.get(
            reverse('booking_detail', args=[booking.pk])
        )
        self.assertNotEqual(response.status_code, 200)