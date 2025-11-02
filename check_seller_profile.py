import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from users.models import User
from sellers.models import SellerProfile

try:
    user = User.objects.get(email='seller@example.com')
    print(f'[OK] User exists: {user.email}')
    print(f'  Role: {user.role}')
    
    try:
        profile = SellerProfile.objects.get(user=user)
        print(f'[OK] Seller profile exists: {profile.business_name}')
        print(f'  Verified: {profile.is_verified}')
        print(f'  Active: {profile.is_active}')
    except SellerProfile.DoesNotExist:
        print('[ERROR] Seller profile does NOT exist for this user')
        print('\nSolution: User needs to create a seller profile at /seller/setup')
        
except User.DoesNotExist:
    print('[ERROR] User seller@example.com does not exist')
except Exception as e:
    print(f'[ERROR] Error: {e}')

