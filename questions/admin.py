from django.contrib import admin
from django.db.models import Count

from .models import Question, Subject


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'is_active', 'monitor_count']
    list_filter = ['is_active']
    search_fields = ['code', 'name']
    # RF1: the monitor <-> subject link is editable here.
    filter_horizontal = ['monitors']

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(num_monitors=Count('monitors'))

    @admin.display(description='Monitors', ordering='num_monitors')
    def monitor_count(self, obj):
        return obj.num_monitors


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'subject', 'author', 'assigned_monitor', 'status',
        'created_at', 'updated_at',
    ]
    list_filter = ['status', 'subject']
    search_fields = ['title', 'description', 'author__username']
    list_select_related = ['subject', 'author', 'assigned_monitor']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'created_at'
