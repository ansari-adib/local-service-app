 
def notification_count(request):
    """
    Makes unread notification count available
    in every template automatically.
    """

    if request.user.is_authenticated:
        count = request.user.notifications.filter(
            is_read=False
        ).count()
        return {'unread_notifications': count}
    return {'unread_notifications': 0}