from django.core.management.base import BaseCommand
from products.models import Category


class Command(BaseCommand):
    help = 'Seed categories into the database'

    def handle(self, *args, **kwargs):
        self.stdout.write('Seeding categories...')

        # Create categories
        categories_data = [
            {'name': 'Electronics', 'slug': 'electronics', 'description': 'Electronic devices and gadgets'},
            {'name': 'Clothing', 'slug': 'clothing', 'description': 'Fashion and apparel'},
            {'name': 'Books', 'slug': 'books', 'description': 'Books and literature'},
            {'name': 'Home & Garden', 'slug': 'home-garden', 'description': 'Home improvement and garden supplies'},
            {'name': 'Toys & Games', 'slug': 'toys-games', 'description': 'Toys, games and entertainment'},
            {'name': 'Sports & Outdoors', 'slug': 'sports-outdoors', 'description': 'Sports equipment and outdoor gear'},
            {'name': 'Beauty & Personal Care', 'slug': 'beauty-personal-care', 'description': 'Beauty products and personal care items'},
            {'name': 'Automotive', 'slug': 'automotive', 'description': 'Car parts and accessories'},
        ]

        created_count = 0
        for cat_data in categories_data:
            category, created = Category.objects.get_or_create(
                slug=cat_data['slug'],
                defaults=cat_data
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created category: {category.name}'))
                created_count += 1
            else:
                self.stdout.write(f'Category already exists: {category.name}')

        self.stdout.write(self.style.SUCCESS(f'\n{created_count} categories created/verified'))
        self.stdout.write(self.style.SUCCESS(f'Total categories in database: {Category.objects.count()}'))

