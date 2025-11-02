from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = 'Create dummy accounts for testing'

    def handle(self, *args, **options):
        self.stdout.write('Creating dummy accounts...')

        # Create superuser
        if not User.objects.filter(email='superuser@example.com').exists():
            superuser = User.objects.create_superuser(
                email='superuser@example.com',
                username='superuser',
                password='superuser',
                first_name='Super',
                last_name='User',
                role='admin'
            )
            self.stdout.write(
                self.style.SUCCESS(f'✓ Created superuser: {superuser.email}')
            )
        else:
            self.stdout.write('⚠ Superuser already exists')

        # Create admin user
        if not User.objects.filter(email='admin@example.com').exists():
            admin = User.objects.create_user(
                email='admin@example.com',
                username='admin',
                password='admin',
                first_name='Admin',
                last_name='User',
                role='admin',
                is_staff=True
            )
            self.stdout.write(
                self.style.SUCCESS(f'✓ Created admin: {admin.email}')
            )
        else:
            self.stdout.write('⚠ Admin already exists')

        # Create sample seller
        if not User.objects.filter(email='seller@example.com').exists():
            seller = User.objects.create_user(
                email='seller@example.com',
                username='seller',
                password='seller123',
                first_name='John',
                last_name='Seller',
                role='seller',
                phone='123-456-7890',
                address='123 Seller St, Commerce City, CC 12345'
            )
            self.stdout.write(
                self.style.SUCCESS(f'✓ Created seller: {seller.email}')
            )
        else:
            self.stdout.write('⚠ Seller already exists')

        # Create sample buyer
        if not User.objects.filter(email='buyer@example.com').exists():
            buyer = User.objects.create_user(
                email='buyer@example.com',
                username='buyer',
                password='buyer123',
                first_name='Jane',
                last_name='Buyer',
                role='buyer',
                phone='098-765-4321',
                address='456 Buyer Ave, Shopping Town, ST 67890'
            )
            self.stdout.write(
                self.style.SUCCESS(f'✓ Created buyer: {buyer.email}')
            )
        else:
            self.stdout.write('⚠ Buyer already exists')

        self.stdout.write('\n' + '='*50)
        self.stdout.write('DUMMY ACCOUNTS SUMMARY:')
        self.stdout.write('='*50)
        self.stdout.write('🔑 Superuser: superuser@example.com / superuser')
        self.stdout.write('👤 Admin: admin@example.com / admin')
        self.stdout.write('💼 Seller: seller@example.com / seller123')
        self.stdout.write('🛒 Buyer: buyer@example.com / buyer123')
        self.stdout.write('='*50)
        self.stdout.write('Django Admin: http://localhost:8000/admin/')
        self.stdout.write('='*50)
