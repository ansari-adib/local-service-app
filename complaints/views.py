from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Complaint
from .forms import ComplaintForm, ComplaintResponseForm
from bookings.models import Booking
from notifications.utils import send_notification


@login_required(login_url='/accounts/login/')
def submit_complaint(request, booking_pk=None):
    """
    Customer or provider submits a complaint.
    Can be linked to a specific booking or standalone.
    """

    booking = None
    if booking_pk:
        booking = get_object_or_404(Booking, pk=booking_pk)

        # Make sure only involved parties can complain
        is_customer = booking.customer == request.user
        is_provider = (
            request.user.is_provider() and
            booking.service.provider.user == request.user
        )
        if not (is_customer or is_provider):
            messages.error(request, 'Access denied.')
            return redirect('dashboard')

    if request.method == 'POST':
        form = ComplaintForm(request.POST)
        if form.is_valid():
            complaint = form.save(commit=False)
            complaint.submitted_by = request.user
            complaint.booking = booking
            complaint.save()

            # Notify admin
            from accounts.models import User
            admins = User.objects.filter(is_staff=True)
            for admin in admins:
                send_notification(
                    user=admin,
                    title='New Complaint Submitted',
                    message=f'A new complaint has been submitted by '
                            f'{request.user.username}: {complaint.subject}',
                    notification_type='complaint'
                )

            messages.success(
                request,
                'Your complaint has been submitted. '
                'We will review it shortly.'
            )

            if request.user.is_customer():
                return redirect('my_complaints')
            else:
                return redirect('provider_complaints')
    else:
        form = ComplaintForm()

    context = {
        'form': form,
        'booking': booking,
    }
    return render(request, 'complaints/submit_complaint.html', context)


@login_required(login_url='/accounts/login/')
def my_complaints(request):
    """
    Customer sees all their submitted complaints.
    """

    if not request.user.is_customer():
        messages.error(request, 'Access denied.')
        return redirect('dashboard')

    complaints = Complaint.objects.filter(
        submitted_by=request.user
    ).select_related('booking__service')

    return render(request, 'complaints/my_complaints.html', {
        'complaints': complaints
    })


@login_required(login_url='/accounts/login/')
def provider_complaints(request):
    """
    Provider sees all their submitted complaints.
    """

    if not request.user.is_provider():
        messages.error(request, 'Access denied.')
        return redirect('dashboard')

    complaints = Complaint.objects.filter(
        submitted_by=request.user
    ).select_related('booking__service')

    return render(request, 'complaints/provider_complaints.html', {
        'complaints': complaints
    })


@login_required(login_url='/accounts/login/')
def complaint_detail(request, pk):
    """
    Detail view for a complaint.
    """

    complaint = get_object_or_404(Complaint, pk=pk)

    # Only the submitter or admin can view
    if complaint.submitted_by != request.user and not request.user.is_staff:
        messages.error(request, 'Access denied.')
        return redirect('dashboard')

    return render(request, 'complaints/complaint_detail.html', {
        'complaint': complaint
    })


@login_required(login_url='/accounts/login/')
def admin_complaints(request):
    """
    Admin views and manages all complaints.
    """

    if not request.user.is_staff:
        messages.error(request, 'Access denied.')
        return redirect('dashboard')

    complaints = Complaint.objects.all().select_related(
        'submitted_by',
        'booking__service'
    )

    # Filter by status
    status_filter = request.GET.get('status', '')
    if status_filter:
        complaints = complaints.filter(status=status_filter)

    open_count = Complaint.objects.filter(
        status=Complaint.STATUS_OPEN
    ).count()

    context = {
        'complaints': complaints,
        'open_count': open_count,
        'status_filter': status_filter,
    }
    return render(request, 'complaints/admin_complaints.html', context)


@login_required(login_url='/accounts/login/')
def admin_complaint_response(request, pk):
    """
    Admin responds to a complaint and updates its status.
    """

    if not request.user.is_staff:
        messages.error(request, 'Access denied.')
        return redirect('dashboard')

    complaint = get_object_or_404(Complaint, pk=pk)

    if request.method == 'POST':
        form = ComplaintResponseForm(request.POST, instance=complaint)
        if form.is_valid():
            form.save()

            # Notify the user who submitted the complaint
            send_notification(
                user=complaint.submitted_by,
                title='Complaint Status Updated',
                message=f'Your complaint "{complaint.subject}" '
                        f'has been updated to: '
                        f'{complaint.get_status_display()}.',
                notification_type='complaint'
            )

            messages.success(
                request,
                'Complaint response saved successfully.'
            )
            return redirect('admin_complaints')
    else:
        form = ComplaintResponseForm(instance=complaint)

    return render(request, 'complaints/admin_complaint_response.html', {
        'complaint': complaint,
        'form': form
    })