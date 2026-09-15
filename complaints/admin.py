from django.contrib import admin
from .models import Complaint


@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display = ['id', 'submitted_by']
    search_fields = ['submitted_by__username']
# from django.contrib import admin
# from .models import Complaint


# @admin.register(Complaint)
# class ComplaintAdmin(admin.ModelAdmin):
#     list_display = ['id', 'submitted_by', 'subject', 'status', 'created_at']
#     list_filter = ['status']
#     search_fields = ['submitted_by__username', 'subject']