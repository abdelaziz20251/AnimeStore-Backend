from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = 'Setup local development accounts for testing'

    def handle(self, *args, **options):
        accounts = [
            {
                'email': 'admin@example.com',
                'username': 'admin',
                'password': 'admin',
                'role': 'admin',
                'is_staff': True,
                'is_superuser': True,
                'first_name': 'Admin',
                'last_name': 'User',
            },
            {
                'email': 'superuser@example.com',
                'username': 'superuser',
                'password': 'superuser',
                'role': 'admin',
                'is_staff': True,
                'is_superuser': True,
                'first_name': 'Super',
                'last_name': 'User',
            },
            {
                'email': 'seller@example.com',
                'username': 'seller',
                'password': 'seller123',
                'role': 'seller',
                'first_name': 'John',
                'last_name': 'Seller',
            },
            {
                'email': 'buyer@example.com',
                'username': 'buyer',
                'password': 'buyer123',
                'role': 'buyer',
                'first_name': 'Jane',
                'last_name': 'Buyer',
            },
        ]

        self.stdout.write(self.style.WARNING('\nSetting up local development accounts...\n'))

        for acc in accounts:
            password = acc.pop('password')
            
            try:
                user, created = User.objects.get_or_create(
                    email=acc['email'],
                    defaults=acc
                )
                
                if created:
                    user.set_password(password)
                    user.save()
                    self.stdout.write(
                        self.style.SUCCESS(f'Created: {acc["email"]} / {password} ({acc["role"]})')
                    )
                else:
                    # Update existing user
                    user.set_password(password)
                    for key, value in acc.items():
                        setattr(user, key, value)
                    user.save()
                    self.stdout.write(
                        self.style.WARNING(f'Updated: {acc["email"]} / {password} ({acc["role"]})')
                    )
                    
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Failed to create {acc["email"]}: {str(e)}')
                )

        self.stdout.write(self.style.SUCCESS('\nLocal setup complete!\n'))
        self.stdout.write(self.style.HTTP_INFO('Accounts created:'))
        self.stdout.write('  • Admin: admin@example.com / admin')
        self.stdout.write('  • Superuser: superuser@example.com / superuser')
        self.stdout.write('  • Seller: seller@example.com / seller123')
        self.stdout.write('  • Buyer: buyer@example.com / buyer123\n')
