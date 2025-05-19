from django.contrib import admin
from .models import OtherPackage

@admin.register(OtherPackage)
class OtherPackageAdmin(admin.ModelAdmin):
    list_display = ('client_name', 'service_type', 'start_time', 'end_time', 'status', 'total_amount')
    list_filter = ('service_type', 'status', 'created_at')
    search_fields = ('client_name', 'description')
    date_hierarchy = 'start_time'
    fieldsets = (
        ('Client Information', {
            'fields': ('client_name', 'created_by')
        }),
        ('Service Details', {
            'fields': ('service_type', 'description', 'total_amount')
        }),
        ('Timing', {
            'fields': ('start_time', 'end_time', 'status')
        }),
    )