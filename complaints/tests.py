from django.test import TestCase, Client
from django.urls import reverse
from datetime import date
from accounts.models import User, CustomerProfile, ProviderProfile
from services.models import ServiceCategory, Service
from bookings.models import Booking
from complaints.models import Complaint


class ComplaintTest(TestCase):
    """Tests for the complaint system."""

    def setUp(self):
        self.client = Client()

        self.customer = User.objects.create_user(
            username='complaint_customer',
            email='cc@test.com',
            password='TestPass@123',
            role=User.ROLE_CUSTOMER
        )
        CustomerProfile.objects.create(user=self.customer)

        self.provider_user = User.objects.create_user(
            username='complaint_provider',
            email='cp@test.com',
            password='TestPass@123',
            role=User.ROLE_PROVIDER
        )
        self.provider_profile = ProviderProfile.objects.create(
            user=self.provider_user,
            city='Delhi',
            experience_years=2
        )

        self.admin = User.objects.create_user(
            username='complaint_admin',
            email='ca@test.com',
            password='TestPass@123',
            role=User.ROLE_ADMIN,
            is_staff=True
        )

        self.category = ServiceCategory.objects.create(
            name='Carpentry',
            is_active=True
        )
        self.service = Service.objects.create(
            provider=self.provider_profile,
            category=self.category,
            name='Furniture Repair',
            description='Fix furniture',
            price=600,
            duration_hours=2,
            is_available=True
        )
        self.booking = Booking.objects.create(
            customer=self.customer,
            service=self.service,
            booking_date=date.today(),
            time_slot='morning',
            address='Test Address',
            city='Delhi',
            status=Booking.STATUS_COMPLETED,
            total_price=600
        )

    def test_customer_can_submit_complaint(self):
        """Customer should be able to submit a complaint."""
        self.client.login(
            username='complaint_customer',
            password='TestPass@123'
        )
        self.client.post(
            reverse('submit_complaint'),
            {
                'subject': 'Poor quality work',
                'description': 'The work was not done properly.'
            }
        )
        self.assertEqual(Complaint.objects.count(), 1)
        complaint = Complaint.objects.first()
        self.assertEqual(complaint.status, Complaint.STATUS_OPEN)

    def test_complaint_linked_to_booking(self):
        """Complaint can be linked to a specific booking."""
        self.client.login(
            username='complaint_customer',
            password='TestPass@123'
        )
        self.client.post(
            reverse(
                'submit_complaint_booking',
                args=[self.booking.pk]
            ),
            {
                'subject': 'Service not completed properly',
                'description': 'Provider left without finishing the work.'
            }
        )
        self.assertEqual(Complaint.objects.count(), 1)
        complaint = Complaint.objects.first()
        self.assertEqual(complaint.booking, self.booking)

    def test_admin_can_respond_to_complaint(self):
        """Admin should be able to respond to a complaint."""
        complaint = Complaint.objects.create(
            submitted_by=self.customer,
            booking=self.booking,
            subject='Test complaint',
            description='Test description',
            status=Complaint.STATUS_OPEN
        )
        self.client.login(
            username='complaint_admin',
            password='TestPass@123'
        )
        self.client.post(
            reverse('admin_complaint_response', args=[complaint.pk]),
            {
                'status': Complaint.STATUS_RESOLVED,
                'admin_response': 'We have investigated and resolved this.'
            }
        )
        complaint.refresh_from_db()
        self.assertEqual(complaint.status, Complaint.STATUS_RESOLVED)

    def test_customer_cannot_access_admin_complaints(self):
        """Customer should not access admin complaints page."""
        self.client.login(
            username='complaint_customer',
            password='TestPass@123'
        )
        response = self.client.get(reverse('admin_complaints'))
        self.assertNotEqual(response.status_code, 200)

    def test_unauthenticated_cannot_submit_complaint(self):
        """Unauthenticated user should not submit a complaint."""
        response = self.client.get(reverse('submit_complaint'))
        self.assertEqual(response.status_code, 302)