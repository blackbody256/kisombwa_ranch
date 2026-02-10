from django.contrib import admin
from .models import Alert


@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    list_display = [
        'title',
        'alert_type',
        'severity',
        'animal',
        'is_read',
        'is_resolved',
        'created_at'
    ]
    list_filter = [
        'alert_type',
        'severity',
        'is_read',
        'is_resolved',
        'created_at'
    ]
    search_fields = ['title', 'message', 'animal__tag_id', 'animal__name']
    readonly_fields = ['id', 'created_at', 'resolved_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Alert Information', {
            'fields': ('id', 'alert_type', 'severity', 'title', 'message', 'animal')
        }),
        ('Status', {
            'fields': ('is_read', 'is_resolved', 'resolved_by', 'resolved_at')
        }),
        ('Metadata', {
            'fields': ('metadata', 'created_at'),
            'classes': ('collapse',)
        }),
    )
