import random
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.core.models import Ranch, Animal
from apps.iot.models import Device

User = get_user_model()

class Command(BaseCommand):
    help = 'Seed database with demo data for Kisombwa Ranch'

    def handle(self, *args, **kwargs):
        self.stdout.write('Seeding database...')
        
        # Create users
        admin, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@kisombwa.com',
                'role': 'admin',
                'is_staff': True,
                'is_superuser': True
            }
        )
        if created:
            admin.set_password('admin123')
            admin.save()
            self.stdout.write(self.style.SUCCESS(f'Created admin user'))
        
        vet, created = User.objects.get_or_create(
            username='vet',
            defaults={
                'email': 'vet@kisombwa.com',
                'role': 'vet',
                'phone_number': '+256700123456'
            }
        )
        if created:
            vet.set_password('vet123')
            vet.save()
            self.stdout.write(self.style.SUCCESS(f'Created vet user'))
        
        worker, created = User.objects.get_or_create(
            username='worker',
            defaults={
                'email': 'worker@kisombwa.com',
                'role': 'worker',
                'phone_number': '+256700789012'
            }
        )
        if created:
            worker.set_password('worker123')
            worker.save()
            self.stdout.write(self.style.SUCCESS(f'Created worker user'))
        
        # Create ranch
        ranch, created = Ranch.objects.get_or_create(
            name='Kisombwa Ranching Scheme',
            defaults={
                'location': 'Kitenga Sub County, Mubende District, Uganda',
                'size_hectares': 2400,
                'owner': admin
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created ranch: {ranch.name}'))

        # Create Devices first, before animals
        # This is a simplified approach, in a real system devices might be pre-registered
        device_ids = [f"IOT-TAG-{i:03d}" for i in range(1, 21)]
        device_pool = []
        for device_id_str in device_ids:
            device, created = Device.objects.get_or_create(
                device_id=device_id_str,
                defaults={
                    'status': 'active',
                    'firmware_version': '1.0.0',
                    'battery_level': random.randint(50, 100),
                    'ranch': ranch
                }
            )
            device_pool.append(device)
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created device: {device.device_id}'))
        
        # Create 20 animals
        breeds = ['Boran', 'Ankole', 'Friesian']
        genders = ['M', 'F']
        statuses = ['active', 'active', 'active', 'sick']  # Weighted towards active
        
        for i in range(len(device_pool)):
            device = device_pool[i]
            tag_id = f"Dowry{i+1:03d}"
            
            # Check if animal already exists or if device is already assigned
            if Animal.objects.filter(tag_id=tag_id).exists() or device.animal is not None:
                continue
            
            birth_date = datetime.now().date() - timedelta(days=random.randint(365, 1825))  # 1-5 years old
            
            animal = Animal.objects.create(
                tag_id=tag_id,
                name=f"Boran #{i+1}",
                breed=random.choice(breeds),
                gender=random.choice(genders),
                birth_date=birth_date,
                status=random.choice(statuses),
            )
            
            # Link the animal to the device
            device.animal = animal
            device.save()
            
            self.stdout.write(self.style.SUCCESS(f'Created animal: {animal.tag_id} and assigned to device {device.device_id}'))
        
        self.stdout.write(self.style.SUCCESS('Database seeding completed!'))
        self.stdout.write(f'Total animals: {Animal.objects.count()}')
        self.stdout.write(f'Total devices: {Device.objects.count()}')
        
