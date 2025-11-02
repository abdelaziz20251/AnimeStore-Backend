import os
import django
from datetime import datetime, timedelta
import random

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.utils import timezone
from orders.models import Order, OrderItem
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Update all orders with randomized dates between Sept 1 - Oct 25, 2025'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be updated without making changes',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        # Set date range: September 1, 2025 to October 25, 2025
        start_date = datetime(2025, 9, 1, 0, 0, 0)
        end_date = datetime(2025, 10, 25, 23, 59, 59)
        
        # Convert to timezone-aware datetimes
        start_date = timezone.make_aware(start_date)
        end_date = timezone.make_aware(end_date)
        
        # Get all orders
        orders = Order.objects.all()
        total = orders.count()
        
        if total == 0:
            self.stdout.write(self.style.WARNING('No orders found to update.'))
            return
        
        self.stdout.write(f'Found {total} orders to update.')
        self.stdout.write(f'Date range: {start_date.date()} to {end_date.date()}')
        
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No changes will be made'))
        
        updated = 0
        for order in orders:
            # Generate random date within range
            total_seconds = int((end_date - start_date).total_seconds())
            random_seconds = random.randint(0, total_seconds)
            new_date = start_date + timedelta(seconds=random_seconds)
            
            if not dry_run:
                order.created_at = new_date
                order.updated_at = new_date + timedelta(hours=random.randint(1, 24))
                order.save()
            
            updated += 1
            if updated % 10 == 0 or updated == total:
                self.stdout.write(f'Updated {updated}/{total} orders...')
        
        if not dry_run:
            self.stdout.write(self.style.SUCCESS(f'\nSuccessfully updated {updated} orders with random dates.'))
            self.stdout.write('Sample of updated orders:')
            
            # Show a sample
            sample_orders = Order.objects.all().order_by('-created_at')[:5]
            for order in sample_orders:
                self.stdout.write(f'  - Order #{order.order_number}: {order.created_at}')
        else:
            self.stdout.write(self.style.WARNING(f'\nDRY RUN: Would have updated {updated} orders'))

