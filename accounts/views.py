from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import (
    CustomerRegistrationForm,
    ProviderRegistrationForm,
    LoginForm,
    CustomerProfileUpdateForm,
    ProviderProfileUpdateForm,
)
from .models import User, CustomerProfile, ProviderProfile


def home(request):
    """Public home page."""
    return render(request, 'home.html')


def register_customer(request):
    """Customer registration view."""

    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            # Create user
            user = form.save(commit=False)
            user.role = User.ROLE_CUSTOMER
            user.phone = form.cleaned_data.get('phone')
            user.save()

            # Create customer profile automatically
            CustomerProfile.objects.create(user=user)

            # Log the user in
            login(request, user)
            messages.success(
                request,
                f'Welcome {user.first_name}! Your account has been created.'
            )
            return redirect('customer_dashboard')
    else:
        form = CustomerRegistrationForm()

    return render(request, 'accounts/register_customer.html', {'form': form})


def register_provider(request):
    """Service provider registration view."""

    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = ProviderRegistrationForm(request.POST)
        if form.is_valid():
            # Create user
            user = form.save(commit=False)
            user.role = User.ROLE_PROVIDER
            user.phone = form.cleaned_data.get('phone')
            user.save()

            # Create provider profile automatically
            ProviderProfile.objects.create(
                user=user,
                bio=form.cleaned_data.get('bio', ''),
                city=form.cleaned_data.get('city', ''),
                experience_years=form.cleaned_data.get('experience_years', 0),
            )

            # Log the user in
            login(request, user)
            messages.success(
                request,
                f'Welcome {user.first_name}! Your provider account has been created.'
            )
            return redirect('provider_dashboard')
    else:
        form = ProviderRegistrationForm()

    return render(request, 'accounts/register_provider.html', {'form': form})


def user_login(request):
    """Login view for all user types."""

    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')

            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {user.first_name or user.username}!')

                # Redirect based on role
                if user.is_admin_user() or user.is_staff:
                    return redirect('admin_dashboard')
                elif user.is_provider():
                    return redirect('provider_dashboard')
                else:
                    return redirect('customer_dashboard')
            else:
                messages.error(request, 'Invalid username or password.')
    else:
        form = LoginForm()

    return render(request, 'accounts/login.html', {'form': form})


def user_logout(request):
    """Logout view."""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('login')


def dashboard(request):
    """
    Generic dashboard redirect based on role.
    """
    if not request.user.is_authenticated:
        return redirect('login')

    if request.user.is_admin_user() or request.user.is_staff:
        return redirect('admin_dashboard')
    elif request.user.is_provider():
        return redirect('provider_dashboard')
    else:
        return redirect('customer_dashboard')


@login_required(login_url='/accounts/login/')
def customer_dashboard(request):
    """Customer dashboard."""

    if not request.user.is_customer():
        messages.error(request, 'Access denied.')
        return redirect('dashboard')

    profile = CustomerProfile.objects.get_or_create(
        user=request.user
    )[0]

    context = {
        'profile': profile,
        'user': request.user,
    }
    return render(request, 'accounts/customer_dashboard.html', context)


@login_required(login_url='/accounts/login/')
def provider_dashboard(request):
    """Provider dashboard."""

    if not request.user.is_provider():
        messages.error(request, 'Access denied.')
        return redirect('dashboard')

    profile = ProviderProfile.objects.get_or_create(
        user=request.user
    )[0]

    context = {
        'profile': profile,
        'user': request.user,
    }
    return render(request, 'accounts/provider_dashboard.html', context)


@login_required(login_url='/accounts/login/')
def admin_dashboard(request):
    """
    Full admin dashboard with platform statistics.
    """

    if not (request.user.is_admin_user() or request.user.is_staff):
        messages.error(request, 'Access denied.')
        return redirect('dashboard')

    from bookings.models import Booking
    from services.models import Service, ServiceCategory
    from reviews.models import Review
    from complaints.models import Complaint

    # User Statistics
    total_customers = User.objects.filter(
        role=User.ROLE_CUSTOMER
    ).count()
    total_providers = User.objects.filter(
        role=User.ROLE_PROVIDER
    ).count()

    # Booking Statistics
    total_bookings = Booking.objects.count()
    pending_bookings = Booking.objects.filter(
        status=Booking.STATUS_PENDING
    ).count()
    completed_bookings = Booking.objects.filter(
        status=Booking.STATUS_COMPLETED
    ).count()
    cancelled_bookings = Booking.objects.filter(
        status=Booking.STATUS_CANCELLED
    ).count()

    # Service Statistics
    total_services = Service.objects.count()
    total_categories = ServiceCategory.objects.count()

    # Review Statistics
    total_reviews = Review.objects.count()

    # Complaint Statistics
    open_complaints = Complaint.objects.filter(
        status=Complaint.STATUS_OPEN
    ).count()
    total_complaints = Complaint.objects.count()

    # Recent Data
    recent_bookings = Booking.objects.select_related(
        'customer',
        'service__provider__user'
    ).order_by('-created_at')[:5]

    recent_complaints = Complaint.objects.select_related(
        'submitted_by'
    ).order_by('-created_at')[:5]

    recent_providers = ProviderProfile.objects.select_related(
        'user'
    ).order_by('-created_at')[:5]

    context = {
        # User stats
        'total_customers': total_customers,
        'total_providers': total_providers,

        # Booking stats
        'total_bookings': total_bookings,
        'pending_bookings': pending_bookings,
        'completed_bookings': completed_bookings,
        'cancelled_bookings': cancelled_bookings,

        # Service stats
        'total_services': total_services,
        'total_categories': total_categories,

        # Review and complaint stats
        'total_reviews': total_reviews,
        'open_complaints': open_complaints,
        'total_complaints': total_complaints,

        # Recent data
        'recent_bookings': recent_bookings,
        'recent_complaints': recent_complaints,
        'recent_providers': recent_providers,
    }
    return render(request, 'accounts/admin_dashboard.html', context)

@login_required(login_url='/accounts/login/')
def update_profile(request):
    """Update profile for customer or provider."""

    user = request.user

    if user.is_customer():
        profile = CustomerProfile.objects.get_or_create(user=user)[0]
        form_class = CustomerProfileUpdateForm
        template = 'accounts/update_profile_customer.html'
    elif user.is_provider():
        profile = ProviderProfile.objects.get_or_create(user=user)[0]
        form_class = ProviderProfileUpdateForm
        template = 'accounts/update_profile_provider.html'
    else:
        return redirect('dashboard')

    if request.method == 'POST':
        form = form_class(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('dashboard')
    else:
        form = form_class(instance=profile)

    return render(request, template, {'form': form})

@login_required(login_url='/accounts/login/')
def admin_users(request):
    """Admin views all users."""

    if not (request.user.is_admin_user() or request.user.is_staff):
        messages.error(request, 'Access denied.')
        return redirect('dashboard')

    role_filter = request.GET.get('role', '')
    users = User.objects.all().order_by('-date_joined')

    if role_filter:
        users = users.filter(role=role_filter)

    context = {
        'users': users,
        'role_filter': role_filter,
    }
    return render(request, 'accounts/admin_users.html', context)


@login_required(login_url='/accounts/login/')
def admin_toggle_user(request, pk):
    """Admin activates or deactivates a user."""

    if not (request.user.is_admin_user() or request.user.is_staff):
        messages.error(request, 'Access denied.')
        return redirect('dashboard')

    user = get_object_or_404(User, pk=pk)

    if user == request.user:
        messages.error(request, 'You cannot deactivate yourself.')
        return redirect('admin_users')

    user.is_active = not user.is_active
    user.save()

    status = 'activated' if user.is_active else 'deactivated'
    messages.success(request, f'User {user.username} has been {status}.')
    return redirect('admin_users')


@login_required(login_url='/accounts/login/')
def admin_verify_provider(request, pk):
    """Admin verifies a service provider."""

    if not (request.user.is_admin_user() or request.user.is_staff):
        messages.error(request, 'Access denied.')
        return redirect('dashboard')

    provider = get_object_or_404(ProviderProfile, pk=pk)
    provider.is_verified = not provider.is_verified
    provider.save()

    status = 'verified' if provider.is_verified else 'unverified'
    messages.success(
        request,
        f'Provider {provider.user.username} has been {status}.'
    )
    return redirect('admin_users')


@login_required(login_url='/accounts/login/')
def admin_all_bookings(request):
    """Admin views all bookings."""

    if not (request.user.is_admin_user() or request.user.is_staff):
        messages.error(request, 'Access denied.')
        return redirect('dashboard')

    from bookings.models import Booking

    status_filter = request.GET.get('status', '')
    bookings = Booking.objects.select_related(
        'customer',
        'service__provider__user',
        'service__category'
    ).order_by('-created_at')

    if status_filter:
        bookings = bookings.filter(status=status_filter)

    context = {
        'bookings': bookings,
        'status_filter': status_filter,
    }
    return render(request, 'accounts/admin_bookings.html', context)


@login_required(login_url='/accounts/login/')
def admin_all_services(request):
    """Admin views all services."""

    if not (request.user.is_admin_user() or request.user.is_staff):
        messages.error(request, 'Access denied.')
        return redirect('dashboard')

    from services.models import Service, ServiceCategory

    services = Service.objects.select_related(
        'provider__user',
        'category'
    ).order_by('-created_at')

    categories = ServiceCategory.objects.all()

    context = {
        'services': services,
        'categories': categories,
    }
    return render(request, 'accounts/admin_services.html', context)