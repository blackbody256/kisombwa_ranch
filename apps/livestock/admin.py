from django.contrib import admin
from .models import Animal, HealthRecord, Vaccination, WeightRecord

@admin.register(Animal)
class AnimalAdmin(admin.ModelAdmin):
    list_display = ['tag_id', 'name', 'breed', 'gender', 'birth_date', 'status', 'created_at']
    list_filter = ['status', 'breed', 'gender']
    search_fields = ['tag_id', 'name']
    readonly_fields = ['qr_code', 'created_at', 'updated_at']

@admin.register(HealthRecord)
class HealthRecordAdmin(admin.ModelAdmin):
    list_display = ['animal', 'date', 'diagnosis', 'severity', 'cost']
    list_filter = ['severity', 'date']
    search_fields = ['animal__tag_id', 'diagnosis']

@admin.register(Vaccination)
class VaccinationAdmin(admin.ModelAdmin):
    list_display = ['animal', 'vaccine_name', 'date_administered', 'next_due_date']
    list_filter = ['date_administered', 'next_due_date']
    search_fields = ['animal__tag_id', 'vaccine_name']

@admin.register(WeightRecord)
class WeightRecordAdmin(admin.ModelAdmin):
    list_display = ['animal', 'date', 'weight']
    list_filter = ['date']
    search_fields = ['animal__tag_id']