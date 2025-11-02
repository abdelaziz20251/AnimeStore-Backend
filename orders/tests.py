from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import Cart, CartItem, Order, OrderItem
from products.models import Product, Category

User = get_user_model()


class CartModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='buyer@example.com',
            username='buyer',
            password='pass123'
        )
        self.seller = User.objects.create_user(
            email='seller@example.com',
            username='seller',
            password='pass123',
            role='seller'
        )
        self.category = Category.objects.create(
            name='Electronics',
            slug='electronics'
        )
        self.product = Product.objects.create(
            seller=self.seller,
            category=self.category,
            name='Laptop',
            slug='laptop',
            description='A great laptop',
            price=999.99,
            stock=10,
            sku='LAP001'
        )
    
    def test_create_cart(self):
        """Test creating a cart"""
        cart = Cart.objects.create(user=self.user)
        self.assertEqual(cart.user, self.user)
        self.assertEqual(cart.total_items, 0)
    
    def test_cart_with_items(self):
        """Test cart with items"""
        cart = Cart.objects.create(user=self.user)
        cart_item = CartItem.objects.create(
            cart=cart,
            product=self.product,
            quantity=2
        )
        self.assertEqual(cart.total_items, 2)
        self.assertEqual(cart_item.subtotal, self.product.price * 2)


class OrderModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='buyer@example.com',
            username='buyer',
            password='pass123'
        )
    
    def test_create_order(self):
        """Test creating an order"""
        order = Order.objects.create(
            user=self.user,
            subtotal=100.00,
            tax=10.00,
            shipping_cost=10.00,
            total=120.00,
            shipping_address='123 Main St',
            shipping_city='New York',
            shipping_state='NY',
            shipping_zip='10001',
            shipping_country='USA',
            phone='1234567890'
        )
        self.assertEqual(order.user, self.user)
        self.assertEqual(order.status, 'pending')
        self.assertIsNotNone(order.order_number)
        self.assertTrue(order.order_number.startswith('ORD-'))
