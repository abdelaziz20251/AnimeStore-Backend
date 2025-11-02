from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from products.models import Category, Product
from decimal import Decimal

User = get_user_model()


class Command(BaseCommand):
    help = 'Set up demo data for the e-commerce platform'

    def handle(self, *args, **kwargs):
        self.stdout.write('Setting up demo data...')

        # Create admin user
        if not User.objects.filter(username='admin').exists():
            admin = User.objects.create_superuser(
                email='admin@example.com',
                username='admin',
                password='admin123',
                first_name='Admin',
                last_name='User'
            )
            self.stdout.write(self.style.SUCCESS(f'[OK] Created admin user (admin/admin123)'))
        else:
            admin = User.objects.get(username='admin')
            self.stdout.write('Admin user already exists')

        # Create seller user
        if not User.objects.filter(username='seller1').exists():
            seller = User.objects.create_user(
                email='seller@example.com',
                username='seller1',
                password='seller123',
                first_name='John',
                last_name='Seller',
                role='seller'
            )
            self.stdout.write(self.style.SUCCESS(f'[OK] Created seller user (seller1/seller123)'))
        else:
            seller = User.objects.get(username='seller1')
            self.stdout.write('Seller user already exists')

        # Create buyer user
        if not User.objects.filter(username='buyer1').exists():
            buyer = User.objects.create_user(
                email='buyer@example.com',
                username='buyer1',
                password='buyer123',
                first_name='Jane',
                last_name='Buyer',
                role='buyer'
            )
            self.stdout.write(self.style.SUCCESS(f'[OK] Created buyer user (buyer1/buyer123)'))
        else:
            self.stdout.write('Buyer user already exists')

        # Create categories
        categories_data = [
            {'name': 'Electronics', 'slug': 'electronics', 'description': 'Electronic devices and gadgets'},
            {'name': 'Clothing', 'slug': 'clothing', 'description': 'Fashion and apparel'},
            {'name': 'Books', 'slug': 'books', 'description': 'Books and literature'},
            {'name': 'Home & Garden', 'slug': 'home-garden', 'description': 'Home improvement and garden supplies'},
        ]

        for cat_data in categories_data:
            category, created = Category.objects.get_or_create(
                slug=cat_data['slug'],
                defaults=cat_data
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'[OK] Created category: {category.name}'))

        # Create demo products
        electronics = Category.objects.get(slug='electronics')
        clothing = Category.objects.get(slug='clothing')
        books = Category.objects.get(slug='books')

        products_data = [
            {
                'name': 'Wireless Headphones',
                'slug': 'wireless-headphones',
                'description': 'High-quality wireless headphones with noise cancellation. Perfect for music lovers and professionals who need to focus.',
                'price': Decimal('99.99'),
                'stock': 50,
                'sku': 'ELEC-001',
                'category': electronics,
                'is_featured': True,
                'image_url': 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=800&h=800&fit=crop',
                'thumbnail_url': 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=400&h=400&fit=crop',
            },
            {
                'name': 'Smart Watch',
                'slug': 'smart-watch',
                'description': 'Feature-rich smartwatch with fitness tracking, heart rate monitor, and GPS. Stay connected and healthy.',
                'price': Decimal('199.99'),
                'stock': 30,
                'sku': 'ELEC-002',
                'category': electronics,
                'is_featured': True,
                'image_url': 'https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=800&h=800&fit=crop',
                'thumbnail_url': 'https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=400&h=400&fit=crop',
            },
            {
                'name': 'Laptop Stand',
                'slug': 'laptop-stand',
                'description': 'Ergonomic aluminum laptop stand with adjustable height. Improve your posture and productivity.',
                'price': Decimal('49.99'),
                'stock': 100,
                'sku': 'ELEC-003',
                'category': electronics,
                'image_url': 'https://images.unsplash.com/photo-1527864550417-7fd91fc51a46?w=800&h=800&fit=crop',
                'thumbnail_url': 'https://images.unsplash.com/photo-1527864550417-7fd91fc51a46?w=400&h=400&fit=crop',
            },
            {
                'name': 'Cotton T-Shirt',
                'slug': 'cotton-tshirt',
                'description': 'Comfortable 100% cotton t-shirt. Soft, breathable, and perfect for everyday wear.',
                'price': Decimal('19.99'),
                'stock': 200,
                'sku': 'CLOTH-001',
                'category': clothing,
                'image_url': 'https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=800&h=800&fit=crop',
                'thumbnail_url': 'https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=400&h=400&fit=crop',
            },
            {
                'name': 'Denim Jeans',
                'slug': 'denim-jeans',
                'description': 'Classic blue denim jeans with modern fit. Durable, stylish, and versatile for any occasion.',
                'price': Decimal('59.99'),
                'stock': 75,
                'sku': 'CLOTH-002',
                'category': clothing,
                'is_featured': True,
                'image_url': 'https://images.unsplash.com/photo-1542272604-787c3835535d?w=800&h=800&fit=crop',
                'thumbnail_url': 'https://images.unsplash.com/photo-1542272604-787c3835535d?w=400&h=400&fit=crop',
            },
            {
                'name': 'Python Programming Book',
                'slug': 'python-programming-book',
                'description': 'Learn Python programming from scratch. Comprehensive guide for beginners and intermediate developers.',
                'price': Decimal('39.99'),
                'stock': 40,
                'sku': 'BOOK-001',
                'category': books,
                'image_url': 'https://images.unsplash.com/photo-1589998059171-988d887df646?w=800&h=800&fit=crop',
                'thumbnail_url': 'https://images.unsplash.com/photo-1589998059171-988d887df646?w=400&h=400&fit=crop',
            },
        ]

        for prod_data in products_data:
            product, created = Product.objects.get_or_create(
                slug=prod_data['slug'],
                defaults={**prod_data, 'seller': seller}
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'[OK] Created product: {product.name}'))

        self.stdout.write(self.style.SUCCESS('\n[SUCCESS] Demo data setup complete!'))
        self.stdout.write('\nLogin credentials:')
        self.stdout.write('  Admin: admin / admin123')
        self.stdout.write('  Seller: seller1 / seller123')
        self.stdout.write('  Buyer: buyer1 / buyer123')

