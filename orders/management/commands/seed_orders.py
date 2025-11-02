import random
from decimal import Decimal
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import Sum
from django.utils import timezone
from orders.models import Order, OrderItem, OrderStatusHistory
from products.models import Product

User = get_user_model()


class Command(BaseCommand):
    help = 'Seed orders for buyer@example.com with products from seller@example.com'
    
    # Shipping addresses for variety
    SHIPPING_ADDRESSES = [
        {
            'address': '123 Main Street, Apt 4B',
            'city': 'New York',
            'state': 'NY',
            'zip': '10001',
            'country': 'USA',
            'phone': '+1-555-0123'
        },
        {
            'address': '456 Oak Avenue, Suite 100',
            'city': 'Los Angeles',
            'state': 'CA',
            'zip': '90001',
            'country': 'USA',
            'phone': '+1-555-0456'
        },
        {
            'address': '789 Pine Road',
            'city': 'Chicago',
            'state': 'IL',
            'zip': '60601',
            'country': 'USA',
            'phone': '+1-555-0789'
        },
    ]
    
    PAYMENT_METHODS = ['card', 'cash_on_delivery', 'paypal', 'bank_transfer']
    
    # Status timeline: pending -> processing -> shipped -> delivered
    STATUS_TIMELINE = {
        'pending': {
            'weight': 20,  # 20% of orders stay pending
            'next_status': 'processing',
        },
        'processing': {
            'weight': 30,  # 30% of orders stay processing
            'next_status': 'shipped',
        },
        'shipped': {
            'weight': 30,  # 30% of orders stay shipped
            'next_status': 'delivered',
        },
        'delivered': {
            'weight': 20,  # 20% of orders are delivered
            'next_status': None,
        },
    }
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=10,
            help='Number of orders to seed (default: 10)'
        )
        parser.add_argument(
            '--buyer-email',
            type=str,
            default='buyer@example.com',
            help='Buyer email (default: buyer@example.com)'
        )
        parser.add_argument(
            '--seller-email',
            type=str,
            default='seller@example.com',
            help='Seller email (default: seller@example.com)'
        )
    
    def handle(self, *args, **options):
        count = options['count']
        buyer_email = options['buyer_email']
        seller_email = options['seller_email']
        
        # Get buyer
        try:
            buyer = User.objects.get(email=buyer_email, role='buyer')
            self.stdout.write(self.style.SUCCESS(f'Found buyer: {buyer.email}'))
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'Buyer {buyer_email} not found. Please create the buyer first.'))
            return
        
        # Get seller products
        try:
            seller = User.objects.get(email=seller_email, role='seller')
            products = Product.objects.filter(seller=seller, is_active=True)
            
            if not products.exists():
                self.stdout.write(self.style.ERROR(f'No active products found for seller {seller_email}.'))
                return
            
            self.stdout.write(self.style.SUCCESS(f'Found {products.count()} products from seller {seller.email}'))
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'Seller {seller_email} not found.'))
            return
        
        # Generate status distribution
        statuses = []
        total_weight = sum(s['weight'] for s in self.STATUS_TIMELINE.values())
        for status, config in self.STATUS_TIMELINE.items():
            count_for_status = int(count * config['weight'] / total_weight)
            statuses.extend([status] * count_for_status)
        
        # Adjust for rounding
        while len(statuses) < count:
            statuses.append('delivered')
        
        random.shuffle(statuses)
        
        created_count = 0
        for idx, order_status in enumerate(statuses[:count], 1):
            # Select random shipping address
            shipping_info = random.choice(self.SHIPPING_ADDRESSES)
            
            # Select 1-3 random products
            num_products = random.randint(1, 3)
            selected_products = list(products.order_by('?')[:num_products])
            
            # Calculate totals
            subtotal = Decimal('0.00')
            items_data = []
            
            for product in selected_products:
                quantity = random.randint(1, 3)
                product_price = product.price
                
                # Apply discount if exists
                if product.discount_percentage > 0:
                    discount_amount = product_price * (product.discount_percentage / 100)
                    product_price = product_price - discount_amount
                
                item_total = product_price * quantity
                subtotal += item_total
                
                items_data.append({
                    'product': product,
                    'quantity': quantity,
                    'price': product_price,
                })
            
            # Calculate tax (10%)
            tax = subtotal * Decimal('0.10')
            
            # Shipping cost (some orders have free shipping)
            shipping_cost = Decimal(random.choice([
                '0.00',  # Free shipping
                '5.99',
                '9.99',
                '15.99'
            ]))
            
            total = subtotal + tax + shipping_cost
            
            # Generate timestamp based on status
            created_at = self._generate_timestamp_for_status(order_status, idx)
            
            # Create order
            order = Order.objects.create(
                user=buyer,
                status=order_status,
                subtotal=subtotal,
                tax=tax,
                shipping_cost=shipping_cost,
                total=total,
                shipping_address=shipping_info['address'],
                shipping_city=shipping_info['city'],
                shipping_state=shipping_info['state'],
                shipping_zip=shipping_info['zip'],
                shipping_country=shipping_info['country'],
                phone=shipping_info['phone'],
                payment_method=random.choice(self.PAYMENT_METHODS),
                payment_status=self._get_payment_status_for_order_status(order_status),
                created_at=created_at,
            )
            
            # Create order items
            for item_data in items_data:
                OrderItem.objects.create(
                    order=order,
                    product=item_data['product'],
                    product_name=item_data['product'].name,
                    product_sku=item_data['product'].sku,
                    price=item_data['price'],
                    quantity=item_data['quantity'],
                    created_at=created_at,
                )
                
                # Reduce stock (simulating actual purchase)
                item_data['product'].stock -= item_data['quantity']
                if item_data['product'].stock < 0:
                    item_data['product'].stock = 0  # Don't go negative
                item_data['product'].save()
            
            # Create status history
            self._create_status_history(order, order_status, buyer, created_at)
            
            self.stdout.write(self.style.SUCCESS(
                f'{idx}. Order {order.order_number} - {order_status.upper()} - '
                f'${float(total):.2f} - {len(items_data)} items'
            ))
            created_count += 1
        
        self.stdout.write(self.style.SUCCESS(f'\n{created_count} orders created successfully!'))
        self.stdout.write(self.style.SUCCESS(f'Buyer: {buyer.email}'))
        self.stdout.write(self.style.SUCCESS(f'Seller: {seller.email}'))
        
        # Print summary by status
        self._print_status_summary(buyer)
    
    def _generate_timestamp_for_status(self, status, order_num):
        """Generate timestamp based on order status."""
        now = timezone.now()
        
        # Orders are spread over the last 30 days
        days_ago = random.randint(1, 30)
        base_datetime = now - timedelta(days=days_ago)
        
        if status == 'delivered':
            # Delivered orders are older
            return base_datetime - timedelta(days=random.randint(3, 7))
        elif status == 'shipped':
            # Shipped orders are a bit older
            return base_datetime - timedelta(days=random.randint(2, 5))
        elif status == 'processing':
            # Processing orders are recent
            return base_datetime - timedelta(days=random.randint(1, 3))
        else:  # pending
            # Pending orders are very recent
            return base_datetime - timedelta(hours=random.randint(1, 48))
    
    def _get_payment_status_for_order_status(self, status):
        """Determine payment status based on order status."""
        if status in ['delivered', 'shipped']:
            return 'completed'
        elif status == 'processing':
            return 'processing'
        else:
            return 'pending'
    
    def _create_status_history(self, order, status, user, created_at):
        """Create status history records based on current status."""
        status_notes = {
            'pending': 'Order received and payment is being processed',
            'processing': 'Order is being prepared for shipment',
            'shipped': 'Order has been shipped',
            'delivered': 'Order has been delivered successfully',
        }
        
        OrderStatusHistory.objects.create(
            order=order,
            status=status,
            notes=status_notes.get(status, 'Status updated'),
            changed_by=user,
            created_at=created_at,
        )
        
        # If delivered, create intermediate statuses
        if status == 'delivered':
            for intermediate_status in ['processing', 'shipped']:
                OrderStatusHistory.objects.create(
                    order=order,
                    status=intermediate_status,
                    notes=status_notes.get(intermediate_status, 'Status updated'),
                    changed_by=user,
                    created_at=created_at - timedelta(days=3 if intermediate_status == 'processing' else 1),
                )
    
    def _print_status_summary(self, buyer):
        """Print summary of orders by status."""
        from orders.models import Order
        
        orders = Order.objects.filter(user=buyer)
        
        self.stdout.write('\n' + '='*60)
        self.stdout.write('ORDER SUMMARY BY STATUS')
        self.stdout.write('='*60)
        
        for status, config in self.STATUS_TIMELINE.items():
            count = orders.filter(status=status).count()
            total_amount = orders.filter(status=status).aggregate(
                total=Sum('total')
            )['total'] or 0
            
            self.stdout.write(
                f'{status.upper()}: {count} orders - Total: ${float(total_amount):.2f}'
            )
        
        total_orders = orders.count()
        total_amount = orders.aggregate(total=Sum('total'))['total'] or 0
        self.stdout.write('-'*60)
        self.stdout.write(f'TOTAL: {total_orders} orders - ${float(total_amount):.2f}')
        self.stdout.write('='*60)

