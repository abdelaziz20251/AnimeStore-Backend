import requests
import random
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from products.models import Category, Product, ProductImage

User = get_user_model()


class Command(BaseCommand):
    help = 'Seed products from real API data for seller@example.com'
    
    # Free API to fetch real electronics products
    API_URL = "https://api.dummyjson.com/products/category/electronics"
    IMAGE_BASE_URL = "https://i0.wp.com/static.photos/blurred/1200x630"
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=6,
            help='Number of products to seed (default: 6)'
        )
        parser.add_argument(
            '--seller-email',
            type=str,
            default='seller@example.com',
            help='Seller email (default: seller@example.com)'
        )
    
    def handle(self, *args, **options):
        count = options['count']
        seller_email = options['seller_email']
        
        # Get seller
        try:
            seller = User.objects.get(email=seller_email, role='seller')
            self.stdout.write(self.style.SUCCESS(f'Found seller: {seller.email}'))
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'Seller {seller_email} not found. Please create the seller first.'))
            return
        
        # Get or create Electronics category
        category, created = Category.objects.get_or_create(
            name='Electronics',
            defaults={
                'slug': 'electronics',
                'description': 'Electronic devices and gadgets'
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created category: {category.name}'))
        else:
            self.stdout.write(f'Using existing category: {category.name}')
        
        # Fetch real products from API
        self.stdout.write('Fetching real electronics products from API...')
        
        try:
            response = requests.get(self.API_URL, timeout=10)
            response.raise_for_status()
            products_data = response.json()
            
            # Get unique products
            all_products = products_data.get('products', [])
            
            if not all_products:
                self.stdout.write(self.style.WARNING('No products found in API response'))
                return
            
            # Shuffle and get random products
            random.shuffle(all_products)
            selected_products = all_products[:count]
            
            created_count = 0
            # Randomly select 2 products to have low stock
            low_stock_indices = set(random.sample(range(len(selected_products)), min(2, len(selected_products))))
            
            for idx, api_product in enumerate(selected_products, 1):
                # Generate image URL using pattern
                image_id = random.randint(100, 999)
                image_url = f"{self.IMAGE_BASE_URL}/{image_id}"
                
                # Determine stock - low stock for 2 products
                if idx - 1 in low_stock_indices:
                    stock = random.randint(1, 5)  # Low stock
                else:
                    stock = api_product.get('stock', random.randint(10, 100))
                
                # Create product
                product = Product.objects.create(
                    seller=seller,
                    category=category,
                    name=api_product.get('title', f'Electronics Product {idx}'),
                    description=api_product.get('description', 'High-quality electronics product'),
                    price=round(api_product.get('price', random.randint(50, 1000)), 2),
                    discount_percentage=round(api_product.get('discountPercentage', random.randint(0, 50)), 2),
                    shipping_fee=round(random.uniform(0, 20), 2),
                    stock=stock,
                    brand=api_product.get('brand', 'TechBrand'),
                    weight=round(random.uniform(0.5, 5.0), 2),
                    tags=api_product.get('tags', ['electronics', 'tech', 'gadget']),
                    technical_specs={
                        'model': api_product.get('model', 'N/A'),
                        'warranty': f"{random.randint(1, 3)} years",
                        'color': random.choice(['Black', 'Silver', 'White', 'Blue']),
                        'features': api_product.get('tags', [])[:3]
                    },
                    refund_policy='30-day money-back guarantee. Free return shipping.',
                    image_url=image_url,
                    thumbnail_url=image_url,
                    is_active=True,
                    is_featured=idx <= 2  # First 2 products are featured
                )
                
                # Add multiple product images
                num_images = random.randint(2, 4)
                for img_idx in range(num_images):
                    img_id = random.randint(100, 999)
                    ProductImage.objects.create(
                        product=product,
                        image_url=f"{self.IMAGE_BASE_URL}/{img_id}",
                        alt_text=f"{product.name} - Image {img_idx + 1}",
                        order=img_idx
                    )
                
                stock_status = "[LOW STOCK]" if product.stock <= 5 else ""
                self.stdout.write(self.style.SUCCESS(
                    f'{idx}. Created: {product.name} - ${product.price} (Stock: {product.stock}) {stock_status}'
                ))
                created_count += 1
            
            self.stdout.write(self.style.SUCCESS(f'\n{created_count} products created successfully!'))
            self.stdout.write(self.style.SUCCESS(f'Seller: {seller.email}'))
            self.stdout.write(self.style.SUCCESS(f'Category: {category.name}'))
            
        except requests.exceptions.RequestException as e:
            self.stdout.write(self.style.ERROR(f'Failed to fetch products from API: {e}'))
            self.stdout.write(self.style.WARNING('Creating products with generated data...'))
            
            # Fallback: Create products with generated data
            self.create_fallback_products(seller, category, count)
    
    def create_fallback_products(self, seller, category, count):
        """Fallback method to create products when API is unavailable."""
        product_names = [
            'Wireless Bluetooth Earbuds Pro',
            'Smart Watch Fitness Tracker',
            'Portable Power Bank 20000mAh',
            'USB-C Fast Charger',
            'Wireless Charging Pad',
            'Laptop Cooling Pad'
        ]
        
        descriptions = [
            'Premium wireless earbuds with active noise cancellation and 30-hour battery life.',
            'Track your fitness goals with heart rate monitor and GPS tracking.',
            'Ultra-fast charging power bank with quick charge 3.0 technology.',
            'Fast charging USB-C cable compatible with all devices.',
            'Charge your phone wirelessly on the go with this portable pad.',
            'Keep your laptop cool with dual silent fans and ergonomic design.'
        ]
        
        prices = [79.99, 149.99, 39.99, 24.99, 29.99, 34.99]
        
        created_count = 0
        # Randomly select 2 products to have low stock
        low_stock_indices = set(random.sample(range(count), min(2, count)))
        
        for idx in range(count):
            image_id = random.randint(100, 999)
            image_url = f"{self.IMAGE_BASE_URL}/{image_id}"
            
            # Determine stock - low stock for 2 products
            if idx in low_stock_indices:
                stock = random.randint(1, 5)  # Low stock
            else:
                stock = random.randint(15, 150)
            
            product = Product.objects.create(
                seller=seller,
                category=category,
                name=product_names[idx % len(product_names)],
                description=descriptions[idx % len(descriptions)],
                price=round(prices[idx % len(prices)] + random.randint(0, 50), 2),
                discount_percentage=round(random.randint(5, 30), 2),
                shipping_fee=round(random.uniform(0, 15), 2),
                stock=stock,
                brand=random.choice(['TechBrand', 'SmartTech', 'ElectroPro', 'GadgetHub']),
                weight=round(random.uniform(0.5, 3.0), 2),
                tags=['electronics', 'tech', 'gadget', 'wireless'] if idx % 2 == 0 else ['electronics', 'tech', 'charging'],
                technical_specs={
                    'warranty': f"{random.randint(1, 2)} years",
                    'color': random.choice(['Black', 'Silver', 'White']),
                    'connectivity': random.choice(['Bluetooth 5.0', 'USB-C', 'Wireless']),
                    'battery': random.choice(['Rechargeable', 'Non-rechargeable'])
                },
                refund_policy='30-day money-back guarantee with free return shipping.',
                image_url=image_url,
                thumbnail_url=image_url,
                is_active=True,
                is_featured=idx < 2
            )
            
            # Add product images
            for img_idx in range(random.randint(2, 3)):
                img_id = random.randint(100, 999)
                ProductImage.objects.create(
                    product=product,
                    image_url=f"{self.IMAGE_BASE_URL}/{img_id}",
                    alt_text=f"{product.name} - Image {img_idx + 1}",
                    order=img_idx
                )
            
            created_count += 1
            stock_status = "[LOW STOCK]" if product.stock <= 5 else ""
            self.stdout.write(self.style.SUCCESS(
                f'{idx + 1}. Created: {product.name} - ${product.price} (Stock: {product.stock}) {stock_status}'
            ))
        
        self.stdout.write(self.style.SUCCESS(f'\n{created_count} products created with generated data!'))

