from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Ranch, Animal, SystemSetting

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
    list_display = ['tag_id', 'name', 'breed', 'gender', 'status', 'ranch']
    list_filter = ['breed', 'gender', 'status']
    search_fields = ['tag_id', 'name']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(SystemSetting)
class SystemSettingAdmin(admin.ModelAdmin):
    list_display = ['label', 'setting_key', 'category', 'setting_type', 'is_enabled', 'updated_at']
    list_filter = ['category', 'setting_type', 'is_enabled']
    search_fields = ['setting_key', 'label', 'description']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('setting_key', 'label', 'description', 'category', 'setting_type')
        }),
        ('Values', {
            'fields': ('boolean_value', 'integer_value', 'decimal_value', 'string_value'),
            'description': 'Set the appropriate value based on the setting type'
        }),
        ('Status', {
            'fields': ('is_enabled', 'created_at', 'updated_at')
        }),
    )