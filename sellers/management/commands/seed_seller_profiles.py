from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from sellers.models import SellerProfile

User = get_user_model()


class Command(BaseCommand):
    help = 'Create seller profiles for all existing seller users'

    def handle(self, *args, **options):
        sellers = User.objects.filter(role='seller')
        
        if not sellers.exists():
            self.stdout.write(self.style.WARNING('No seller users found. Run setup_local first.'))
            return
        
        created_count = 0
        updated_count = 0
        
        for seller in sellers:
            try:
                profile, created = SellerProfile.objects.get_or_create(
                    user=seller,
                    defaults={
                        'business_name': f"{seller.first_name} {seller.last_name} Store",
                        'business_description': f"Welcome to {seller.first_name}'s online store. We offer quality products at great prices!",
                        'business_email': seller.email,
                        'business_phone': '+1-555-0100',
                        'business_address': '123 Seller Street',
                        'business_city': 'Commerce City',
                        'business_state': 'CA',
                        'business_zip': '90210',
                        'business_country': 'USA',
                        'tax_id': 'TAX-123456789',
                        'business_license': 'BL-987654321',
                        'bank_account_holder': f"{seller.first_name} {seller.last_name}",
                        'bank_account_number': '1234567890',
                        'bank_routing_number': '987654321',
                        'bank_name': 'Commerce Bank',
                        'bank_address': '456 Bank Avenue, Finance City, FC 12345',
                        'is_verified': True,
                        'is_active': True,
                    }
                )
                
                if created:
                    created_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(f'Created profile for {seller.email}')
                    )
                else:
                    # Update existing profile to ensure it's verified
                    profile.is_verified = True
                    profile.is_active = True
                    profile.save()
                    updated_count += 1
                    self.stdout.write(
                        self.style.WARNING(f'Updated profile for {seller.email}')
                    )
                    
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Failed to create/update profile for {seller.email}: {str(e)}')
                )
        
        self.stdout.write(self.style.SUCCESS(
            f'\n✓ Created {created_count} seller profiles'
        ))
        if updated_count > 0:
            self.stdout.write(self.style.SUCCESS(f'✓ Updated {updated_count} seller profiles'))
        
        self.stdout.write(self.style.SUCCESS('\nAll seller profiles are ready!'))

