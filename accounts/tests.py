from django.test import TestCase, Client
from django.urls import reverse
from accounts.models import User, CustomerProfile, ProviderProfile


class UserRegistrationTest(TestCase):
    """Tests for customer and provider registration."""

    def setUp(self):
        """Runs before every test."""
        self.client = Client()

    def test_customer_registration_valid(self):
        """Valid customer registration should succeed."""
        response = self.client.post(reverse('register_customer'), {
            'first_name': 'Test',
            'last_name': 'Customer',
            'username': 'testcustomer',
            'email': 'customer@test.com',
            'phone': '9876543210',
            'password1': 'TestPass@123',
            'password2': 'TestPass@123',
        })
        self.assertEqual(User.objects.filter(username='testcustomer').count(), 1)
        user = User.objects.get(username='testcustomer')
        self.assertEqual(user.role, User.ROLE_CUSTOMER)

    def test_customer_profile_created_automatically(self):
        """CustomerProfile should be created automatically on registration."""
        self.client.post(reverse('register_customer'), {
            'first_name': 'Test',
            'last_name': 'Customer',
            'username': 'testcustomer2',
            'email': 'customer2@test.com',
            'phone': '9876543211',
            'password1': 'TestPass@123',
            'password2': 'TestPass@123',
        })
        user = User.objects.get(username='testcustomer2')
        self.assertTrue(
            CustomerProfile.objects.filter(user=user).exists()
        )

    def test_provider_registration_valid(self):
        """Valid provider registration should succeed."""
        self.client.post(reverse('register_provider'), {
            'first_name': 'Test',
            'last_name': 'Provider',
            'username': 'testprovider',
            'email': 'provider@test.com',
            'phone': '9876543212',
            'city': 'Delhi',
            'bio': 'Experienced electrician',
            'experience_years': 5,
            'password1': 'TestPass@123',
            'password2': 'TestPass@123',
        })
        user = User.objects.get(username='testprovider')
        self.assertEqual(user.role, User.ROLE_PROVIDER)

    def test_provider_profile_created_automatically(self):
        """ProviderProfile should be created automatically on registration."""
        self.client.post(reverse('register_provider'), {
            'first_name': 'Test',
            'last_name': 'Provider',
            'username': 'testprovider2',
            'email': 'provider2@test.com',
            'phone': '9876543213',
            'city': 'Mumbai',
            'bio': 'Plumber',
            'experience_years': 3,
            'password1': 'TestPass@123',
            'password2': 'TestPass@123',
        })
        user = User.objects.get(username='testprovider2')
        self.assertTrue(
            ProviderProfile.objects.filter(user=user).exists()
        )

    def test_duplicate_email_rejected(self):
        """Registration with duplicate email should fail."""
        User.objects.create_user(
            username='existing',
            email='duplicate@test.com',
            password='TestPass@123'
        )
        response = self.client.post(reverse('register_customer'), {
            'first_name': 'New',
            'last_name': 'User',
            'username': 'newuser',
            'email': 'duplicate@test.com',
            'phone': '9876543214',
            'password1': 'TestPass@123',
            'password2': 'TestPass@123',
        })
        self.assertEqual(
            User.objects.filter(email='duplicate@test.com').count(), 1
        )

    def test_password_mismatch_rejected(self):
        """Registration with mismatched passwords should fail."""
        response = self.client.post(reverse('register_customer'), {
            'first_name': 'Test',
            'last_name': 'User',
            'username': 'testuser3',
            'email': 'test3@test.com',
            'phone': '9876543215',
            'password1': 'TestPass@123',
            'password2': 'WrongPass@123',
        })
        self.assertEqual(
            User.objects.filter(username='testuser3').count(), 0
        )


class UserLoginTest(TestCase):
    """Tests for user login."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='logintest',
            email='login@test.com',
            password='TestPass@123',
            role=User.ROLE_CUSTOMER
        )
        CustomerProfile.objects.create(user=self.user)

    def test_valid_login(self):
        """Valid credentials should log user in."""
        response = self.client.post(reverse('login'), {
            'username': 'logintest',
            'password': 'TestPass@123',
        })
        self.assertRedirects(response, reverse('customer_dashboard'))

    def test_invalid_password(self):
        """Wrong password should not log user in."""
        response = self.client.post(reverse('login'), {
            'username': 'logintest',
            'password': 'WrongPassword',
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid username or password')

    def test_invalid_username(self):
        """Non-existent username should not log user in."""
        response = self.client.post(reverse('login'), {
            'username': 'nobody',
            'password': 'TestPass@123',
        })
        self.assertEqual(response.status_code, 200)

    def test_logout(self):
        """Logged in user should be able to logout."""
        self.client.login(username='logintest', password='TestPass@123')
        response = self.client.get(reverse('logout'))
        self.assertRedirects(response, reverse('login'))


class RoleBasedAccessTest(TestCase):
    """Tests for role-based access control."""

    def setUp(self):
        self.client = Client()

        self.customer = User.objects.create_user(
            username='customer1',
            email='c1@test.com',
            password='TestPass@123',
            role=User.ROLE_CUSTOMER
        )
        CustomerProfile.objects.create(user=self.customer)

        self.provider = User.objects.create_user(
            username='provider1',
            email='p1@test.com',
            password='TestPass@123',
            role=User.ROLE_PROVIDER
        )
        ProviderProfile.objects.create(user=self.provider)

    def test_customer_cannot_access_provider_dashboard(self):
        """Customer should not access provider dashboard."""
        self.client.login(username='customer1', password='TestPass@123')
        response = self.client.get(reverse('provider_dashboard'))
        self.assertNotEqual(response.status_code, 200)

    def test_provider_cannot_access_customer_dashboard(self):
        """Provider should not access customer dashboard."""
        self.client.login(username='provider1', password='TestPass@123')
        response = self.client.get(reverse('customer_dashboard'))
        self.assertNotEqual(response.status_code, 200)

    def test_unauthenticated_cannot_access_dashboard(self):
        """Unauthenticated user should be redirected to login."""
        response = self.client.get(reverse('customer_dashboard'))
        self.assertRedirects(
            response,
            '/accounts/login/?next=/accounts/customer/dashboard/'
        )

    def test_unauthenticated_cannot_access_provider_dashboard(self):
        """Unauthenticated user cannot access provider dashboard."""
        response = self.client.get(reverse('provider_dashboard'))
        self.assertEqual(response.status_code, 302)