from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Ranch, Animal

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'role', 'is_staff']
    list_filter = ['role', 'is_staff', 'is_active']
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Ranch Info', {'fields': ('role', 'phone_number')}),
    )

@admin.register(Ranch)
class RanchAdmin(admin.ModelAdmin):
    list_display = ['name', 'location', 'size_hectares', 'owner']
    search_fields = ['name', 'location']

@admin.register(Animal)
class AnimalAdmin(admin.ModelAdmin):
    list_display = ['tag_id', 'name', 'breed', 'gender', 'status', 'assigned_device_id']
    list_filter = ['breed', 'gender', 'status']
    search_fields = ['tag_id', 'name']

    def assigned_device_id(self, obj):
        try:
            return obj.assigned_device.device_id
        except Exception:
            return '-'
    assigned_device_id.short_description = 'Device'
    readonly_fields = ['created_at', 'updated_at']
