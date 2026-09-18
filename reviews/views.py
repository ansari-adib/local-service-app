from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Avg
from .models import Review
from .forms import ReviewForm
from bookings.models import Booking
from accounts.models import ProviderProfile


@login_required(login_url='/accounts/login/')
def add_review(request, booking_pk):
    """
    Customer adds a review for a completed booking.
    Only one review allowed per booking.
    """

    if not request.user.is_customer():
        messages.error(request, 'Only customers can leave reviews.')
        return redirect('dashboard')

    booking = get_object_or_404(
        Booking,
        pk=booking_pk,
        customer=request.user,
        status=Booking.STATUS_COMPLETED
    )

    # Check if review already exists
    if hasattr(booking, 'review'):
        messages.warning(
            request,
            'You have already reviewed this booking.'
        )
        return redirect('booking_detail', pk=booking_pk)

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.booking = booking
            review.customer = request.user
            review.save()

            # Update provider average rating
            update_provider_rating(booking.service.provider)

            messages.success(
                request,
                'Thank you! Your review has been submitted.'
            )
            return redirect('booking_detail', pk=booking_pk)
    else:
        form = ReviewForm()

    context = {
        'form': form,
        'booking': booking,
    }
    return render(request, 'reviews/add_review.html', context)


@login_required(login_url='/accounts/login/')
def my_reviews(request):
    """
    Customer sees all their submitted reviews.
    """

    if not request.user.is_customer():
        messages.error(request, 'Access denied.')
        return redirect('dashboard')

    reviews = Review.objects.filter(
        customer=request.user
    ).select_related(
        'booking__service__provider__user',
        'booking__service__category'
    )

    return render(request, 'reviews/my_reviews.html', {
        'reviews': reviews
    })


@login_required(login_url='/accounts/login/')
def provider_reviews(request):
    """
    Provider sees all reviews for their services.
    """

    if not request.user.is_provider():
        messages.error(request, 'Access denied.')
        return redirect('dashboard')

    provider = get_object_or_404(ProviderProfile, user=request.user)

    reviews = Review.objects.filter(
        booking__service__provider=provider
    ).select_related(
        'customer',
        'booking__service'
    )

    context = {
        'reviews': reviews,
        'provider': provider,
    }
    return render(request, 'reviews/provider_reviews.html', context)


def update_provider_rating(provider):
    """
    Recalculates and updates provider average rating.
    Called every time a new review is submitted.
    """

    reviews = Review.objects.filter(
        booking__service__provider=provider
    )

    if reviews.exists():
        avg = reviews.aggregate(Avg('rating'))['rating__avg']
        provider.average_rating = round(avg, 2)
        provider.total_reviews = reviews.count()
        provider.save()