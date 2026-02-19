from django.core.management.base import BaseCommand
from apps.core.models import SystemSetting


class Command(BaseCommand):
    help = 'Seed default system settings'

    def handle(self, *args, **options):
        self.stdout.write('Seeding default system settings...')
        
        # Alert Settings
        alert_settings = [
            {
                'setting_key': 'enable_health_alerts',
                'label': 'Enable Health Alerts',
                'description': 'Send alerts when animals show signs of illness or health concerns',
                'category': 'alerts',
                'setting_type': 'boolean',
                'boolean_value': True,
                'is_enabled': True,
            },
            {
                'setting_key': 'enable_vaccination_alerts',
                'label': 'Enable Vaccination Alerts',
                'description': 'Notify when vaccinations are due or overdue',
                'category': 'alerts',
                'setting_type': 'boolean',
                'boolean_value': True,
                'is_enabled': True,
            },
            {
                'setting_key': 'enable_geofence_alerts',
                'label': 'Enable Geofence Alerts',
                'description': 'Alert when animals leave designated areas',
                'category': 'alerts',
                'setting_type': 'boolean',
                'boolean_value': True,
                'is_enabled': True,
            },
            {
                'setting_key': 'enable_battery_alerts',
                'label': 'Enable Battery Alerts',
                'description': 'Notify when IoT device batteries are low',
                'category': 'alerts',
                'setting_type': 'boolean',
                'boolean_value': True,
                'is_enabled': True,
            },
            {
                'setting_key': 'enable_temperature_alerts',
                'label': 'Enable Temperature Alerts',
                'description': 'Alert when animal body temperature is abnormal',
                'category': 'alerts',
                'setting_type': 'boolean',
                'boolean_value': True,
                'is_enabled': True,
            },
            {
                'setting_key': 'enable_ai_prediction_alerts',
                'label': 'Enable AI Prediction Alerts',
                'description': 'Send alerts based on AI model predictions',
                'category': 'alerts',
                'setting_type': 'boolean',
                'boolean_value': True,
                'is_enabled': True,
            },
        ]
        
        # Threshold Settings
        threshold_settings = [
            {
                'setting_key': 'battery_low_threshold',
                'label': 'Low Battery Threshold (%)',
                'description': 'Battery level below which to trigger low battery alerts',
                'category': 'thresholds',
                'setting_type': 'integer',
                'integer_value': 20,
                'is_enabled': True,
            },
            {
                'setting_key': 'battery_critical_threshold',
                'label': 'Critical Battery Threshold (%)',
                'description': 'Battery level below which to trigger critical battery alerts',
                'category': 'thresholds',
                'setting_type': 'integer',
                'integer_value': 10,
                'is_enabled': True,
            },
            {
                'setting_key': 'temperature_high_threshold',
                'label': 'High Temperature Threshold (°C)',
                'description': 'Body temperature above which to trigger temperature alerts',
                'category': 'thresholds',
                'setting_type': 'decimal',
                'decimal_value': 40.0,
                'is_enabled': True,
            },
            {
                'setting_key': 'temperature_low_threshold',
                'label': 'Low Temperature Threshold (°C)',
                'description': 'Body temperature below which to trigger temperature alerts',
                'category': 'thresholds',
                'setting_type': 'decimal',
                'decimal_value': 37.5,
                'is_enabled': True,
            },
            {
                'setting_key': 'ai_prediction_confidence_threshold',
                'label': 'AI Prediction Confidence Threshold',
                'description': 'Minimum confidence level to trigger prediction-based alerts (0.0 - 1.0)',
                'category': 'thresholds',
                'setting_type': 'decimal',
                'decimal_value': 0.80,
                'is_enabled': True,
            },
            {
                'setting_key': 'vaccination_reminder_days',
                'label': 'Vaccination Reminder Days',
                'description': 'Number of days before vaccination to send reminder alerts',
                'category': 'thresholds',
                'setting_type': 'integer',
                'integer_value': 7,
                'is_enabled': True,
            },
        ]
        
        # Notification Settings
        notification_settings = [
            {
                'setting_key': 'enable_email_notifications',
                'label': 'Enable Email Notifications',
                'description': 'Send alert notifications via email',
                'category': 'notifications',
                'setting_type': 'boolean',
                'boolean_value': False,
                'is_enabled': False,
            },
            {
                'setting_key': 'enable_sms_notifications',
                'label': 'Enable SMS Notifications',
                'description': 'Send alert notifications via SMS',
                'category': 'notifications',
                'setting_type': 'boolean',
                'boolean_value': False,
                'is_enabled': False,
            },
            {
                'setting_key': 'notification_email',
                'label': 'Notification Email Address',
                'description': 'Primary email address for receiving notifications',
                'category': 'notifications',
                'setting_type': 'string',
                'string_value': '',
                'is_enabled': True,
            },
        ]
        
        # General Settings
        general_settings = [
            {
                'setting_key': 'ranch_name',
                'label': 'Ranch Name',
                'description': 'Official name of the ranch',
                'category': 'general',
                'setting_type': 'string',
                'string_value': 'Kisombwa Ranching Scheme',
                'is_enabled': True,
            },
            {
                'setting_key': 'ranch_location',
                'label': 'Ranch Location',
                'description': 'Physical location of the ranch',
                'category': 'general',
                'setting_type': 'string',
                'string_value': 'Mubende District, Uganda',
                'is_enabled': True,
            },
            {
                'setting_key': 'ranch_size_hectares',
                'label': 'Ranch Size (Hectares)',
                'description': 'Total size of the ranch in hectares',
                'category': 'general',
                'setting_type': 'integer',
                'integer_value': 2400,
                'is_enabled': True,
            },
            {
                'setting_key': 'auto_generate_alerts',
                'label': 'Auto-Generate Alerts',
                'description': 'Automatically generate alerts from system data',
                'category': 'general',
                'setting_type': 'boolean',
                'boolean_value': True,
                'is_enabled': True,
            },
            {
                'setting_key': 'alert_retention_days',
                'label': 'Alert Retention Period (Days)',
                'description': 'Number of days to keep resolved alerts before archiving',
                'category': 'general',
                'setting_type': 'integer',
                'integer_value': 30,
                'is_enabled': True,
            },
        ]
        
        all_settings = alert_settings + threshold_settings + notification_settings + general_settings
        
        created_count = 0
        updated_count = 0
        
        for setting_data in all_settings:
            setting, created = SystemSetting.objects.update_or_create(
                setting_key=setting_data['setting_key'],
                defaults=setting_data
            )
            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'✓ Created: {setting.label}'))
            else:
                updated_count += 1
                self.stdout.write(self.style.WARNING(f'↻ Updated: {setting.label}'))
        
        self.stdout.write(self.style.SUCCESS(f'\nSeeding completed!'))
        self.stdout.write(f'Created: {created_count} settings')
        self.stdout.write(f'Updated: {updated_count} settings')
        self.stdout.write(f'Total: {SystemSetting.objects.count()} settings in database')
