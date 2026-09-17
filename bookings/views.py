from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Booking
from .forms import BookingForm, BookingRejectionForm
from services.models import Service
from accounts.models import ProviderProfile
from notifications.utils import (
    notify_booking_received,
    notify_booking_accepted,
    notify_booking_rejected,
    notify_booking_completed,
    notify_booking_cancelled,
)


# ─── CUSTOMER VIEWS ───────────────────────────────────────────


@login_required(login_url='/accounts/login/')
def create_booking(request, service_pk):
    """
    Customer creates a booking for a specific service.
    """

    if not request.user.is_customer():
        messages.error(request, 'Only customers can book services.')
        return redirect('dashboard')

    service = get_object_or_404(Service, pk=service_pk, is_available=True)
    provider = service.provider

    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():

            # Prevent booking own service if user is also a provider
            booking = form.save(commit=False)
            booking.customer = request.user
            booking.service = service
            booking.total_price = service.price
            booking.status = Booking.STATUS_PENDING
            booking.save()

            # Send notification to provider
            notify_booking_received(booking)

            messages.success(
                request,
                'Booking submitted successfully! '
                'Waiting for provider confirmation.'
            )
            return redirect('my_bookings')
    else:
        form = BookingForm()

    context = {
        'form': form,
        'service': service,
        'provider': provider,
    }
    return render(request, 'bookings/create_booking.html', context)


@login_required(login_url='/accounts/login/')
def my_bookings(request):
    """
    Customer sees all their bookings.
    """

    if not request.user.is_customer():
        messages.error(request, 'Access denied.')
        return redirect('dashboard')

    bookings = Booking.objects.filter(
        customer=request.user
    ).select_related(
        'service__provider__user',
        'service__category'
    )

    # Separate by status for tabs
    pending = bookings.filter(status=Booking.STATUS_PENDING)
    accepted = bookings.filter(status=Booking.STATUS_ACCEPTED)
    completed = bookings.filter(status=Booking.STATUS_COMPLETED)
    cancelled = bookings.filter(
        status__in=[Booking.STATUS_CANCELLED, Booking.STATUS_REJECTED]
    )

    context = {
        'bookings': bookings,
        'pending': pending,
        'accepted': accepted,
        'completed': completed,
        'cancelled': cancelled,
    }
    return render(request, 'bookings/my_bookings.html', context)


@login_required(login_url='/accounts/login/')
def booking_detail(request, pk):
    """
    Detail view for a single booking.
    Accessible by the customer or the service provider.
    """

    booking = get_object_or_404(Booking, pk=pk)

    # Only the customer or provider involved can view
    is_customer = booking.customer == request.user
    is_provider = (
        request.user.is_provider() and
        booking.service.provider.user == request.user
    )

    if not (is_customer or is_provider or request.user.is_staff):
        messages.error(request, 'Access denied.')
        return redirect('dashboard')

    # Check if review already exists
    has_review = hasattr(booking, 'review')

    context = {
        'booking': booking,
        'is_customer': is_customer,
        'is_provider': is_provider,
        'has_review': has_review,
    }
    return render(request, 'bookings/booking_detail.html', context)


@login_required(login_url='/accounts/login/')
def cancel_booking(request, pk):
    """
    Customer cancels a pending or accepted booking.
    """

    if not request.user.is_customer():
        messages.error(request, 'Access denied.')
        return redirect('dashboard')

    booking = get_object_or_404(
        Booking,
        pk=pk,
        customer=request.user
    )

    if not booking.can_be_cancelled_by_customer():
        messages.error(
            request,
            'This booking cannot be cancelled at this stage.'
        )
        return redirect('booking_detail', pk=pk)

    if request.method == 'POST':
        booking.status = Booking.STATUS_CANCELLED
        booking.save()

        # Notify provider
        notify_booking_cancelled(booking)

        messages.success(request, 'Booking cancelled successfully.')
        return redirect('my_bookings')

    return render(request, 'bookings/cancel_booking.html', {
        'booking': booking
    })


# ─── PROVIDER VIEWS ───────────────────────────────────────────


@login_required(login_url='/accounts/login/')
def provider_bookings(request):
    """
    Provider sees all bookings for their services.
    """

    if not request.user.is_provider():
        messages.error(request, 'Access denied.')
        return redirect('dashboard')

    provider = get_object_or_404(ProviderProfile, user=request.user)

    bookings = Booking.objects.filter(
        service__provider=provider
    ).select_related(
        'customer',
        'service__category'
    )

    # Separate by status
    pending = bookings.filter(status=Booking.STATUS_PENDING)
    active = bookings.filter(
        status__in=[Booking.STATUS_ACCEPTED, Booking.STATUS_IN_PROGRESS]
    )
    completed = bookings.filter(status=Booking.STATUS_COMPLETED)
    rejected = bookings.filter(
        status__in=[Booking.STATUS_REJECTED, Booking.STATUS_CANCELLED]
    )

    context = {
        'bookings': bookings,
        'pending': pending,
        'active': active,
        'completed': completed,
        'rejected': rejected,
        'provider': provider,
    }
    return render(request, 'bookings/provider_bookings.html', context)


@login_required(login_url='/accounts/login/')
def accept_booking(request, pk):
    """
    Provider accepts a pending booking.
    """

    if not request.user.is_provider():
        messages.error(request, 'Access denied.')
        return redirect('dashboard')

    provider = get_object_or_404(ProviderProfile, user=request.user)
    booking = get_object_or_404(
        Booking,
        pk=pk,
        service__provider=provider
    )

    if not booking.can_be_accepted_by_provider():
        messages.error(request, 'This booking cannot be accepted.')
        return redirect('provider_bookings')

    booking.status = Booking.STATUS_ACCEPTED
    booking.save()

    # Notify customer
    notify_booking_accepted(booking)

    messages.success(
        request,
        f'Booking #{booking.id} has been accepted.'
    )
    return redirect('provider_bookings')


@login_required(login_url='/accounts/login/')
def reject_booking(request, pk):
    """
    Provider rejects a pending booking with a reason.
    """

    if not request.user.is_provider():
        messages.error(request, 'Access denied.')
        return redirect('dashboard')

    provider = get_object_or_404(ProviderProfile, user=request.user)
    booking = get_object_or_404(
        Booking,
        pk=pk,
        service__provider=provider
    )

    if not booking.can_be_accepted_by_provider():
        messages.error(request, 'This booking cannot be rejected.')
        return redirect('provider_bookings')

    if request.method == 'POST':
        form = BookingRejectionForm(request.POST)
        if form.is_valid():
            booking.status = Booking.STATUS_REJECTED
            booking.rejection_reason = form.cleaned_data['rejection_reason']
            booking.save()

            # Notify customer
            notify_booking_rejected(booking)

            messages.success(request, f'Booking #{booking.id} has been rejected.')
            return redirect('provider_bookings')
    else:
        form = BookingRejectionForm()

    return render(request, 'bookings/reject_booking.html', {
        'booking': booking,
        'form': form
    })


@login_required(login_url='/accounts/login/')
def complete_booking(request, pk):
    """
    Provider marks a booking as completed.
    """

    if not request.user.is_provider():
        messages.error(request, 'Access denied.')
        return redirect('dashboard')

    provider = get_object_or_404(ProviderProfile, user=request.user)
    booking = get_object_or_404(
        Booking,
        pk=pk,
        service__provider=provider
    )

    if not booking.can_be_completed_by_provider():
        messages.error(request, 'This booking cannot be marked as completed.')
        return redirect('provider_bookings')

    if request.method == 'POST':
        booking.status = Booking.STATUS_COMPLETED
        booking.save()

        # Notify customer
        notify_booking_completed(booking)

        messages.success(
            request,
            f'Booking #{booking.id} marked as completed.'
        )
        return redirect('provider_bookings')

    return render(request, 'bookings/complete_booking.html', {
        'booking': booking
    })
@login_required(login_url='/accounts/login/')
def customer_dashboard(request):
    """Customer dashboard."""

    if not request.user.is_customer():
        messages.error(request, 'Access denied.')
        return redirect('dashboard')

    profile = CustomerProfile.objects.get_or_create(
        user=request.user
    )[0]

    # Import here to avoid circular imports
    from bookings.models import Booking

    bookings = Booking.objects.filter(customer=request.user)

    context = {
        'profile': profile,
        'user': request.user,
        'total_bookings': bookings.count(),
        'completed_bookings': bookings.filter(
            status=Booking.STATUS_COMPLETED
        ).count(),
        'pending_bookings': bookings.filter(
            status=Booking.STATUS_PENDING
        ).count(),
        'cancelled_bookings': bookings.filter(
            status=Booking.STATUS_CANCELLED
        ).count(),
    }
    return render(request, 'accounts/customer_dashboard.html', context)