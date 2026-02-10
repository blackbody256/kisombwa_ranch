from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
import random
from apps.alerts.models import Alert
from apps.livestock.models import Animal


class Command(BaseCommand):
    help = 'Generate sample alerts for testing the alerts dashboard'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=20,
            help='Number of sample alerts to generate',
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear all existing alerts before generating new ones',
        )

    def handle(self, *args, **options):
        count = options['count']
        clear_existing = options['clear']

        if clear_existing:
            deleted_count = Alert.objects.all().count()
            Alert.objects.all().delete()
            self.stdout.write(self.style.WARNING(f'Cleared {deleted_count} existing alerts'))

        # Get some animals to associate with alerts
        animals = list(Animal.objects.all()[:10])
        if not animals:
            self.stdout.write(self.style.ERROR('No animals found in database. Please add some animals first.'))
            return

        # Define sample alert templates
        alert_templates = [
            {
                'alert_type': 'health',
                'severity': 'high',
                'title': 'Animal Showing Signs of Illness',
                'message': 'Animal {tag} is showing symptoms of illness. Immediate veterinary attention recommended.',
                'metadata': {'symptoms': ['lethargy', 'loss of appetite'], 'temperature': '40.5°C'}
            },
            {
                'alert_type': 'vaccination',
                'severity': 'medium',
                'title': 'Vaccination Due Soon',
                'message': 'Animal {tag} is due for vaccination in 3 days.',
                'metadata': {'vaccine_type': 'FMD', 'due_date': (timezone.now() + timedelta(days=3)).isoformat()}
            },
            {
                'alert_type': 'battery',
                'severity': 'medium',
                'title': 'Low Device Battery',
                'message': 'IoT device for animal {tag} has low battery (15%).',
                'metadata': {'battery_level': 15, 'device_id': 'DEV-001'}
            },
            {
                'alert_type': 'battery',
                'severity': 'high',
                'title': 'Critical Device Battery',
                'message': 'IoT device for animal {tag} has critically low battery (5%).',
                'metadata': {'battery_level': 5, 'device_id': 'DEV-002'}
            },
            {
                'alert_type': 'temperature',
                'severity': 'high',
                'title': 'High Body Temperature',
                'message': 'Animal {tag} has elevated body temperature of 41.2°C.',
                'metadata': {'temperature': 41.2, 'normal_range': '38.5-39.5'}
            },
            {
                'alert_type': 'weight',
                'severity': 'medium',
                'title': 'Weight Loss Detected',
                'message': 'Animal {tag} has lost 15% of body weight in the last month.',
                'metadata': {'current_weight': 340, 'previous_weight': 400, 'change_percent': -15}
            },
            {
                'alert_type': 'geofence',
                'severity': 'high',
                'title': 'Geofence Breach',
                'message': 'Animal {tag} has left the designated grazing area.',
                'metadata': {'location': 'Outside Zone A', 'coordinates': {'lat': -1.234, 'lng': 36.567}}
            },
            {
                'alert_type': 'estrus',
                'severity': 'low',
                'title': 'Heat Cycle Detected',
                'message': 'Animal {tag} is showing signs of estrus.',
                'metadata': {'cycle_day': 21, 'recommended_action': 'Schedule breeding'}
            },
            {
                'alert_type': 'behavior',
                'severity': 'medium',
                'title': 'Abnormal Behavior Detected',
                'message': 'Animal {tag} is showing unusual behavior patterns.',
                'metadata': {'behavior': 'reduced movement', 'duration': '2 hours'}
            },
            {
                'alert_type': 'device',
                'severity': 'high',
                'title': 'Device Malfunction',
                'message': 'IoT device for animal {tag} is not responding.',
                'metadata': {'device_id': 'DEV-003', 'last_seen': (timezone.now() - timedelta(hours=4)).isoformat()}
            },
            {
                'alert_type': 'prediction',
                'severity': 'high',
                'title': 'High Risk Prediction',
                'message': 'AI model predicts high risk of illness for animal {tag} (confidence: 92%).',
                'metadata': {'confidence': 0.92, 'risk_factors': ['temperature', 'activity_level']}
            },
            {
                'alert_type': 'prediction',
                'severity': 'medium',
                'title': 'Health Risk Alert',
                'message': 'AI model predicts moderate health risk for animal {tag} (confidence: 75%).',
                'metadata': {'confidence': 0.75, 'risk_factors': ['weight_loss', 'behavior']}
            },
        ]

        created_count = 0
        for i in range(count):
            template = random.choice(alert_templates)
            animal = random.choice(animals)
            
            # Randomize the creation time (within last 7 days)
            days_ago = random.randint(0, 7)
            hours_ago = random.randint(0, 23)
            created_at = timezone.now() - timedelta(days=days_ago, hours=hours_ago)
            
            # Randomize read/resolved status (most recent are unread/unresolved)
            is_read = days_ago > 2 and random.random() > 0.5
            is_resolved = days_ago > 4 and random.random() > 0.7
            
            # Create the alert
            alert = Alert(
                animal=animal,
                alert_type=template['alert_type'],
                severity=template['severity'],
                title=template['title'],
                message=template['message'].format(tag=animal.tag_id),
                metadata=template['metadata'],
                is_read=is_read,
                is_resolved=is_resolved,
                created_at=created_at,
            )
            
            if is_resolved:
                alert.resolved_at = created_at + timedelta(hours=random.randint(1, 24))
            
            alert.save()
            created_count += 1

        self.stdout.write(self.style.SUCCESS(f'Successfully generated {created_count} sample alerts'))
        
        # Display summary
        stats = {
            'total': Alert.objects.count(),
            'unread': Alert.objects.filter(is_read=False).count(),
            'unresolved': Alert.objects.filter(is_resolved=False).count(),
            'critical': Alert.objects.filter(severity='critical').count(),
            'high': Alert.objects.filter(severity='high').count(),
            'medium': Alert.objects.filter(severity='medium').count(),
            'low': Alert.objects.filter(severity='low').count(),
        }
        
        self.stdout.write('\nAlert Summary:')
        self.stdout.write(f'  Total Alerts: {stats["total"]}')
        self.stdout.write(f'  Unread: {stats["unread"]}')
        self.stdout.write(f'  Unresolved: {stats["unresolved"]}')
        self.stdout.write(f'  Critical: {stats["critical"]}')
        self.stdout.write(f'  High: {stats["high"]}')
        self.stdout.write(f'  Medium: {stats["medium"]}')
        self.stdout.write(f'  Low: {stats["low"]}')
