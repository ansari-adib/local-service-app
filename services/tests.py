from django.test import TestCase, Client
from django.urls import reverse
from accounts.models import User, ProviderProfile, CustomerProfile
from services.models import ServiceCategory, Service


class ServiceCategoryTest(TestCase):
    """Tests for service categories."""

    def setUp(self):
        self.category = ServiceCategory.objects.create(
            name='Electrical',
            description='All electrical work',
            is_active=True
        )

    def test_category_created(self):
        """Category should be created correctly."""
        self.assertEqual(ServiceCategory.objects.count(), 1)
        self.assertEqual(self.category.name, 'Electrical')

    def test_inactive_category(self):
        """Inactive category should exist but not show publicly."""
        inactive = ServiceCategory.objects.create(
            name='Inactive Cat',
            is_active=False
        )
        active_count = ServiceCategory.objects.filter(
            is_active=True
        ).count()
        self.assertEqual(active_count, 1)


class ServiceTest(TestCase):
    """Tests for service listings."""

    def setUp(self):
        self.client = Client()

        # Create provider user
        self.provider_user = User.objects.create_user(
            username='provider_svc',
            email='psvc@test.com',
            password='TestPass@123',
            role=User.ROLE_PROVIDER
        )
        self.provider_profile = ProviderProfile.objects.create(
            user=self.provider_user,
            city='Delhi',
            experience_years=5
        )

        # Create customer user
        self.customer_user = User.objects.create_user(
            username='customer_svc',
            email='csvc@test.com',
            password='TestPass@123',
            role=User.ROLE_CUSTOMER
        )
        CustomerProfile.objects.create(user=self.customer_user)

        # Create category
        self.category = ServiceCategory.objects.create(
            name='Plumbing',
            is_active=True
        )

    def test_provider_can_add_service(self):
        """Provider should be able to add a service."""
        self.client.login(
            username='provider_svc',
            password='TestPass@123'
        )
        response = self.client.post(reverse('add_service'), {
            'category': self.category.pk,
            'name': 'Pipe Repair',
            'description': 'Fix broken pipes',
            'price': 500,
            'duration_hours': 2,
            'is_available': True,
        })
        self.assertEqual(Service.objects.count(), 1)
        self.assertEqual(Service.objects.first().name, 'Pipe Repair')

    def test_customer_cannot_add_service(self):
        """Customer should not be able to add a service."""
        self.client.login(
            username='customer_svc',
            password='TestPass@123'
        )
        response = self.client.post(reverse('add_service'), {
            'category': self.category.pk,
            'name': 'Unauthorized Service',
            'description': 'This should not be added',
            'price': 100,
            'duration_hours': 1,
        })
        self.assertEqual(Service.objects.count(), 0)

    def test_service_list_page_loads(self):
        """Service list page should load for anyone."""
        response = self.client.get(reverse('service_list'))
        self.assertEqual(response.status_code, 200)

    def test_service_search(self):
        """Service search should filter correctly."""
        Service.objects.create(
            provider=self.provider_profile,
            category=self.category,
            name='Pipe Leak Fix',
            description='Fix pipe leaks',
            price=300,
            duration_hours=1,
            is_available=True
        )
        response = self.client.get(
            reverse('service_list') + '?query=Pipe'
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Pipe Leak Fix')

    def test_unavailable_service_not_shown(self):
        """Unavailable services should not show in public list."""
        Service.objects.create(
            provider=self.provider_profile,
            category=self.category,
            name='Hidden Service',
            description='Should not show',
            price=100,
            duration_hours=1,
            is_available=False
        )
        response = self.client.get(reverse('service_list'))
        self.assertNotContains(response, 'Hidden Service')