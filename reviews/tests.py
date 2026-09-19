from django.test import TestCase, Client
from django.urls import reverse
from datetime import date, timedelta
from accounts.models import User, CustomerProfile, ProviderProfile
from services.models import ServiceCategory, Service
from bookings.models import Booking
from reviews.models import Review


class ReviewTest(TestCase):
    """Tests for the review and rating system."""

    def setUp(self):
        self.client = Client()

        self.customer = User.objects.create_user(
            username='review_customer',
            email='rc@test.com',
            password='TestPass@123',
            role=User.ROLE_CUSTOMER
        )
        CustomerProfile.objects.create(user=self.customer)

        self.provider_user = User.objects.create_user(
            username='review_provider',
            email='rp@test.com',
            password='TestPass@123',
            role=User.ROLE_PROVIDER
        )
        self.provider_profile = ProviderProfile.objects.create(
            user=self.provider_user,
            city='Delhi',
            experience_years=2
        )

        self.category = ServiceCategory.objects.create(
            name='AC Repair',
            is_active=True
        )
        self.service = Service.objects.create(
            provider=self.provider_profile,
            category=self.category,
            name='AC Installation',
            description='Install AC unit',
            price=1500,
            duration_hours=2,
            is_available=True
        )

        self.completed_booking = Booking.objects.create(
            customer=self.customer,
            service=self.service,
            booking_date=date.today(),
            time_slot='morning',
            address='Test Address',
            city='Delhi',
            status=Booking.STATUS_COMPLETED,
            total_price=1500
        )

        self.pending_booking = Booking.objects.create(
            customer=self.customer,
            service=self.service,
            booking_date=date.today() + timedelta(days=3),
            time_slot='afternoon',
            address='Test Address',
            city='Delhi',
            status=Booking.STATUS_PENDING,
            total_price=1500
        )

    def test_customer_can_review_completed_booking(self):
        """Customer should be able to review a completed booking."""
        self.client.login(
            username='review_customer',
            password='TestPass@123'
        )
        self.client.post(
            reverse('add_review', args=[self.completed_booking.pk]),
            {
                'rating': 5,
                'comment': 'Excellent service!'
            }
        )
        self.assertEqual(Review.objects.count(), 1)
        review = Review.objects.first()
        self.assertEqual(review.rating, 5)

    def test_cannot_review_pending_booking(self):
        """Customer should not be able to review a pending booking."""
        self.client.login(
            username='review_customer',
            password='TestPass@123'
        )
        response = self.client.post(
            reverse('add_review', args=[self.pending_booking.pk]),
            {
                'rating': 4,
                'comment': 'Good'
            }
        )
        self.assertEqual(Review.objects.count(), 0)

    def test_cannot_submit_duplicate_review(self):
        """Customer should not be able to review same booking twice."""
        Review.objects.create(
            booking=self.completed_booking,
            customer=self.customer,
            rating=4,
            comment='Good service'
        )
        self.client.login(
            username='review_customer',
            password='TestPass@123'
        )
        self.client.post(
            reverse('add_review', args=[self.completed_booking.pk]),
            {
                'rating': 2,
                'comment': 'Changed my mind'
            }
        )
        self.assertEqual(Review.objects.count(), 1)

    def test_provider_rating_updates_after_review(self):
        """Provider average rating should update after review submitted."""
        self.client.login(
            username='review_customer',
            password='TestPass@123'
        )
        self.client.post(
            reverse('add_review', args=[self.completed_booking.pk]),
            {
                'rating': 4,
                'comment': 'Good work'
            }
        )
        self.provider_profile.refresh_from_db()
        self.assertEqual(self.provider_profile.average_rating, 4.00)
        self.assertEqual(self.provider_profile.total_reviews, 1)