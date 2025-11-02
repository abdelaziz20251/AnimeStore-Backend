# Django Backend — E-Commerce MVP

Django 5 + Django REST Framework 3.15 backend for the e-commerce platform.

## 🏗️ Architecture

### Django Apps

- **users** — Custom user model with role-based access (buyer/seller/admin)
- **products** — Product catalog, categories, reviews
- **orders** — Shopping cart, orders, order status tracking
- **sellers** — Seller profiles, payouts
- **analytics** — Product views, search queries, cart activity logs
- **adminpanel** — Admin interface customizations

## 🚀 Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Start development server
python manage.py runserver
```

## 🔧 Configuration

Edit `.env` file:

```env
SECRET_KEY=your-secret-key
DEBUG=True
DB_NAME=ecommerce_db
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432
CORS_ALLOWED_ORIGINS=http://localhost:3000
```

## 📡 API Endpoints

### Authentication
- `POST /api/auth/register` — Register new user
- `POST /api/auth/login` — Login (get JWT tokens)
- `POST /api/auth/refresh` — Refresh access token
- `POST /api/auth/logout` — Logout

### Products
- `GET /api/products/` — List products (paginated)
- `GET /api/products/{id}/` — Get product details
- `POST /api/products/` — Create product (seller only)
- `PUT /api/products/{id}/` — Update product (seller only)
- `DELETE /api/products/{id}/` — Delete product (seller only)

### Cart & Orders
- `GET /api/cart/` — Get user's cart
- `POST /api/cart/add/` — Add item to cart
- `DELETE /api/cart/remove/{item_id}/` — Remove item from cart
- `POST /api/orders/` — Create order from cart
- `GET /api/orders/` — List user's orders
- `GET /api/orders/{id}/` — Get order details

### Sellers
- `GET /api/sellers/dashboard/` — Seller dashboard (seller only)
- `GET /api/sellers/products/` — Seller's products
- `GET /api/sellers/orders/` — Orders for seller's products

## 🧪 Testing

```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test users
python manage.py test products

# With coverage
coverage run --source='.' manage.py test
coverage report
coverage html  # Generate HTML report
```

## 🔒 Security

- **JWT Authentication** via djangorestframework-simplejwt
- **CORS** configured via django-cors-headers
- **Role-Based Access Control** (RBAC) in User model
- **Password validation** with Django validators
- **HTTPS** required in production

## 📊 Database Models

### User
- Custom user model extending AbstractUser
- Fields: email (unique), role (buyer/seller/admin), phone, address

### Product
- Fields: name, slug, description, price, stock, sku, brand, category
- Relations: seller (User), category (Category), images, reviews

### Order
- Fields: order_number, status, subtotal, tax, shipping_cost, total
- Relations: user (User), items (OrderItem)
- Status: pending → processing → shipped → delivered

### Cart
- One-to-one with User
- Contains CartItems (product + quantity)

## 🚢 Deployment

### Production Settings
```python
DEBUG = False
ALLOWED_HOSTS = ['api.domain.com']
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
```

### Gunicorn
```bash
gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 4
```

### Docker
```bash
docker build -t ecommerce-backend .
docker run -p 8000:8000 ecommerce-backend
```

## 📝 Admin Interface

Access Django admin at http://localhost:8000/admin

Default superuser credentials (change after first login):
- Username: admin
- Password: (set during `createsuperuser`)

## 🔗 Useful Commands

```bash
# Create new Django app
python manage.py startapp appname

# Make migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic

# Shell
python manage.py shell
```

