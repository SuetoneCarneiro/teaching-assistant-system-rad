from django.contrib import admin

from .models import OfficeHour


@admin.register(OfficeHour)
class OfficeHourAdmin(admin.ModelAdmin):
    list_display = ['monitor', 'subject', 'weekday', 'start_time', 'end_time']
    list_filter = ['weekday', 'subject']
    search_fields = ['monitor__username', 'subject__code']
    list_select_related = ['monitor', 'subject']
