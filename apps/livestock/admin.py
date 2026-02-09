from django.contrib import admin
from apps.core.models import Animal
from .models import HealthRecord, Vaccination, WeightRecord


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