from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Notification


@login_required(login_url='/accounts/login/')
def notification_list(request):
    """
    Shows all notifications for the logged-in user.
    """

    notifications = Notification.objects.filter(
        user=request.user
    )

    unread_count = notifications.filter(is_read=False).count()

    context = {
        'notifications': notifications,
        'unread_count': unread_count,
    }
    return render(request, 'notifications/notification_list.html', context)


@login_required(login_url='/accounts/login/')
def mark_as_read(request, pk):
    """
    Marks a single notification as read.
    """

    notification = get_object_or_404(
        Notification,
        pk=pk,
        user=request.user
    )
    notification.is_read = True
    notification.save()
    return redirect('notification_list')


@login_required(login_url='/accounts/login/')
def mark_all_read(request):
    """
    Marks all notifications as read for this user.
    """

    Notification.objects.filter(
        user=request.user,
        is_read=False
    ).update(is_read=True)

    messages.success(request, 'All notifications marked as read.')
    return redirect('notification_list')


@login_required(login_url='/accounts/login/')
def delete_notification(request, pk):
    """
    Deletes a single notification.
    """

    notification = get_object_or_404(
        Notification,
        pk=pk,
        user=request.user
    )
    notification.delete()
    return redirect('notification_list')