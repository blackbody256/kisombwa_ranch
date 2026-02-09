import random
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.core.models import Ranch, Animal

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
        
        # Create 20 animals
        breeds = ['Boran', 'Ankole', 'Friesian']
        genders = ['M', 'F']
        statuses = ['active', 'active', 'active', 'sick']  # Weighted towards active
        
        for i in range(1, 21):
            tag_id = f"Dowry{i:03d}"
            
            # Check if animal already exists
            if Animal.objects.filter(tag_id=tag_id).exists():
                continue
            
            birth_date = datetime.now().date() - timedelta(days=random.randint(365, 1825))  # 1-5 years old
            
            animal = Animal.objects.create(
                tag_id=tag_id,
                name=f"Boran #{i}",
                breed=random.choice(breeds),
                gender=random.choice(genders),
                birth_date=birth_date,
                status=random.choice(statuses),
                ranch_id=ranch.name
            )
            
            self.stdout.write(self.style.SUCCESS(f'Created animal: {animal.tag_id}'))
        
        self.stdout.write(self.style.SUCCESS('Database seeding completed!'))
        self.stdout.write(f'Total animals: {Animal.objects.count()}')