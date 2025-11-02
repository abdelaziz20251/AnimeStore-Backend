from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import Category, Product, ProductReview

User = get_user_model()


class CategoryModelTest(TestCase):
    def test_create_category(self):
        """Test creating a category"""
        category = Category.objects.create(
            name='Electronics',
            slug='electronics',
            description='Electronic products'
        )
        self.assertEqual(category.name, 'Electronics')
        self.assertEqual(str(category), 'Electronics')
    
    def test_category_with_parent(self):
        """Test creating a subcategory"""
        parent = Category.objects.create(name='Electronics', slug='electronics')
        child = Category.objects.create(
            name='Laptops',
            slug='laptops',
            parent=parent
        )
        self.assertEqual(child.parent, parent)


class ProductModelTest(TestCase):
    def setUp(self):
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
    
    def test_create_product(self):
        """Test creating a product"""
        product = Product.objects.create(
            seller=self.seller,
            category=self.category,
            name='Laptop',
            slug='laptop',
            description='A great laptop',
            price=999.99,
            stock=10,
            sku='LAP001'
        )
        self.assertEqual(product.name, 'Laptop')
        self.assertEqual(product.seller, self.seller)
        self.assertTrue(product.in_stock)
    
    def test_product_out_of_stock(self):
        """Test product out of stock property"""
        product = Product.objects.create(
            seller=self.seller,
            category=self.category,
            name='Laptop',
            slug='laptop',
            description='A great laptop',
            price=999.99,
            stock=0,
            sku='LAP001'
        )
        self.assertFalse(product.in_stock)


class ProductReviewModelTest(TestCase):
    def setUp(self):
        self.seller = User.objects.create_user(
            email='seller@example.com',
            username='seller',
            password='pass123',
            role='seller'
        )
        self.buyer = User.objects.create_user(
            email='buyer@example.com',
            username='buyer',
            password='pass123',
            role='buyer'
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
    
    def test_create_review(self):
        """Test creating a product review"""
        review = ProductReview.objects.create(
            product=self.product,
            user=self.buyer,
            rating=5,
            title='Great product',
            comment='Really satisfied with this purchase'
        )
        self.assertEqual(review.rating, 5)
        self.assertEqual(review.product, self.product)
        self.assertEqual(review.user, self.buyer)
