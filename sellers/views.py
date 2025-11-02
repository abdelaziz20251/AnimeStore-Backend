from rest_framework import viewsets, views, filters, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Sum, Count, Avg, Q, F
from django.db.models.functions import TruncDate
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from .models import SellerProfile, SellerPayout
from .serializers import SellerProfileSerializer, SellerPayoutSerializer
from products.models import Product
from orders.models import Order, OrderItem, Refund, OrderStatusHistory


class IsSellerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow sellers to edit their own profile.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated and request.user.role == 'seller'
    
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user == request.user


class SellerProfileViewSet(viewsets.ModelViewSet):
    """ViewSet for Seller Profile operations."""
    
    queryset = SellerProfile.objects.all()
    serializer_class = SellerProfileSerializer
    permission_classes = [IsSellerOrReadOnly]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.user.is_authenticated and self.request.user.role == 'seller':
            return queryset.filter(user=self.request.user)
        return queryset.filter(is_active=True, is_verified=True)
    
    def perform_create(self, serializer):
        """Create seller profile and associate with current user."""
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['get', 'patch'], permission_classes=[permissions.IsAuthenticated])
    def my_profile(self, request):
        """Get or update the current seller's profile."""
        if request.user.role != 'seller':
            return Response(
                {'error': 'Only sellers can access this endpoint.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            profile = SellerProfile.objects.get(user=request.user)
        except SellerProfile.DoesNotExist:
            return Response(
                {'error': 'Seller profile not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        if request.method == 'GET':
            serializer = self.get_serializer(profile)
            return Response(serializer.data)
        
        elif request.method == 'PATCH':
            serializer = self.get_serializer(profile, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def dashboard(self, request):
        """Get comprehensive seller dashboard analytics."""
        
        if request.user.role != 'seller':
            return Response(
                {'error': 'Only sellers can access this endpoint.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            seller_profile = SellerProfile.objects.get(user=request.user)
        except SellerProfile.DoesNotExist:
            return Response(
                {'error': 'Seller profile not found. Please complete your seller registration.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Get date range from query params (default to last 365 days to show all data)
        from datetime import datetime
        days = int(request.query_params.get('days', 365))
        
        # Initialize now for use in calculations
        now = timezone.now()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        
        try:
            start_date_str = request.query_params.get('start_date')
            end_date_str = request.query_params.get('end_date')
            
            if start_date_str and end_date_str:
                # Custom date range - parse dates and make timezone-aware
                start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
                
                # Create naive datetimes
                start_datetime = datetime.combine(start_date, datetime.min.time())
                end_datetime = datetime.combine(end_date, datetime.max.time())
                
                # Make them timezone-aware
                start_datetime = timezone.make_aware(start_datetime)
                end_datetime = timezone.make_aware(end_datetime)
            else:
                # Use days parameter
                start_datetime = today_start - timedelta(days=days)
                end_datetime = now
                start_date = (today_start - timedelta(days=days)).date()
                end_date = now.date()
        except (ValueError, TypeError) as e:
            # Invalid date format, use default (365 days to show all data)
            start_datetime = today_start - timedelta(days=365)
            end_datetime = now
            start_date = (today_start - timedelta(days=365)).date()
            end_date = now.date()
        
        # Get time ranges for week-over-week comparison
        seven_days_ago = today_start - timedelta(days=7)
        fourteen_days_ago = today_start - timedelta(days=14)
        
        # Get all seller's products
        products = Product.objects.filter(seller=request.user)
        product_ids = list(products.values_list('id', flat=True))
        
        # If no products, return empty dashboard
        if not product_ids:
            dashboard_data = {
                'seller_info': {
                    'business_name': seller_profile.business_name,
                    'is_verified': seller_profile.is_verified,
                    'average_rating': float(seller_profile.average_rating or 0),
                    'total_reviews': seller_profile.total_reviews or 0,
                    'member_since': seller_profile.created_at,
                },
                'overview': {
                    'total_products': 0,
                    'active_products': 0,
                    'out_of_stock': 0,
                    'total_orders': 0,
                    'orders_to_fulfill': 0,
                    'total_revenue': 0.0,
                },
                'orders_by_status': {
                    'pending': 0,
                    'processing': 0,
                    'shipped': 0,
                    'delivered': 0,
                },
                'recent_performance': {
                    'last_30_days': {'orders': 0, 'revenue': 0.0},
                    'this_week_orders': 0,
                    'last_week_orders': 0,
                    'week_over_week_change': 0.0,
                },
                'daily_revenue_chart': [],
                'top_products': [],
                'low_stock_alerts': [],
                'recent_orders': [],
                'payouts': {'pending': 0.0, 'completed': 0.0, 'available': 0.0}
            }
            return Response(dashboard_data)
        
        # Orders containing seller's products
        order_items = OrderItem.objects.filter(product_id__in=product_ids)
        order_ids = order_items.values_list('order_id', flat=True).distinct()
        orders = Order.objects.filter(id__in=order_ids)
        
        # === OVERVIEW METRICS ===
        total_products = products.count()
        active_products = products.filter(is_active=True).count()
        # Count products with stock less than or equal to 0
        out_of_stock = products.filter(stock__lte=0).count()
        
        # Filter orders by date range - this filters the data based on the selected date range
        orders_in_range = orders.filter(created_at__gte=start_datetime, created_at__lte=end_datetime)
        order_items_in_range = order_items.filter(order__in=orders_in_range)
        
        # Total orders and revenue within date range
        total_orders = orders_in_range.count()
        total_revenue = order_items_in_range.aggregate(
            total=Sum(F('price') * F('quantity'))
        )['total'] or 0
        
        # Orders by status (within date range)
        pending_orders = orders_in_range.filter(status='pending').count()
        processing_orders = orders_in_range.filter(status='processing').count()
        shipped_orders = orders_in_range.filter(status='shipped').count()
        delivered_orders = orders_in_range.filter(status='delivered').count()
        
        # Orders that need action (pending or processing)
        orders_to_fulfill = pending_orders + processing_orders
        
        # === RECENT ANALYTICS (within date range) ===
        recent_orders = orders_in_range
        recent_revenue = order_items_in_range.aggregate(
            total=Sum(F('price') * F('quantity'))
        )['total'] or 0
        
        recent_orders_count = recent_orders.count()
        
        # Week over week comparison (always use last 7 days from today, not filtered by date range)
        # This week: last 7 days (including today)
        # Last week: 8-14 days ago (previous 7-day period, excluding the last 7 days)
        this_week_start = today_start - timedelta(days=7)
        this_week_orders = orders.filter(created_at__gte=this_week_start).count()
        
        last_week_start = today_start - timedelta(days=14)
        last_week_orders = orders.filter(
            created_at__gte=last_week_start,
            created_at__lt=this_week_start
        ).count()
        
        # === DAILY REVENUE CHART (within date range) ===
        daily_revenue = order_items_in_range.annotate(
            date=TruncDate('order__created_at')
        ).values('date').annotate(
            revenue=Sum(F('price') * F('quantity')),
            orders=Count('order_id', distinct=True)
        ).order_by('date')
        
        # === TOP SELLING PRODUCTS ===
        top_products = order_items_in_range.values(
            'product_id',
            'product_name'
        ).annotate(
            total_sold=Sum('quantity'),
            revenue=Sum(F('price') * F('quantity'))
        ).order_by('-total_sold')[:5]
        
        # === LOW STOCK ALERTS ===
        low_stock_products = products.filter(
            is_active=True,
            stock__lte=10,
            stock__gt=0
        ).values('id', 'name', 'stock', 'price')[:10]
        
        # === RECENT ORDERS (Last 10 within date range) ===
        recent_orders_list = []
        for order in orders_in_range.order_by('-created_at')[:10]:
            # Get items for this seller in this order
            seller_items = order_items_in_range.filter(order=order)
            order_total = seller_items.aggregate(
                total=Sum(F('price') * F('quantity'))
            )['total'] or 0
            
            recent_orders_list.append({
                'id': order.id,
                'order_number': order.order_number,
                'status': order.status,
                'total': float(order_total),
                'items_count': seller_items.count(),
                'created_at': order.created_at,
                'customer_name': f"{order.user.first_name} {order.user.last_name}".strip() or order.user.email
            })
        
        # === RATING AND REVIEWS ===
        avg_rating = seller_profile.average_rating or 0
        total_reviews = seller_profile.total_reviews or 0
        
        # === PAYOUT INFORMATION ===
        pending_payout = SellerPayout.objects.filter(
            seller=request.user,
            status='pending'
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        total_payouts = SellerPayout.objects.filter(
            seller=request.user,
            status='completed'
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        # Available balance is total revenue minus all payouts
        # Ensure balance doesn't go negative (shouldn't happen, but safety check)
        available_balance = max(0, float(total_revenue) - float(pending_payout) - float(total_payouts))
        
        # Construct response
        dashboard_data = {
            'date_range': {
                'start_date': str(start_date),
                'end_date': str(end_date),
                'days': days if start_date_str is None else None,
            },
            'seller_info': {
                'business_name': seller_profile.business_name,
                'is_verified': seller_profile.is_verified,
                'average_rating': float(avg_rating),
                'total_reviews': total_reviews,
                'member_since': seller_profile.created_at,
            },
            'overview': {
                'total_products': total_products,
                'active_products': active_products,
                'out_of_stock': out_of_stock,
                'total_orders': total_orders,
                'orders_to_fulfill': orders_to_fulfill,
                'total_revenue': float(total_revenue),
            },
            'orders_by_status': {
                'pending': pending_orders,
                'processing': processing_orders,
                'shipped': shipped_orders,
                'delivered': delivered_orders,
            },
            'recent_performance': {
                'last_30_days': {
                    'orders': recent_orders_count,
                    'revenue': float(recent_revenue),
                },
                'this_week_orders': this_week_orders,
                'last_week_orders': last_week_orders,
                'week_over_week_change': (
                    ((this_week_orders - last_week_orders) / last_week_orders * 100)
                    if last_week_orders > 0 
                    else 100.0 if this_week_orders > 0 else 0.0
                ),
            },
            'daily_revenue_chart': list(daily_revenue),
            'top_products': list(top_products),
            'low_stock_alerts': list(low_stock_products),
            'recent_orders': recent_orders_list,
            'payouts': {
                'pending': float(pending_payout),
                'completed': float(total_payouts),
                'available': available_balance,
            }
        }
        
        return Response(dashboard_data)
    
    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def analytics(self, request):
        """Get detailed analytics for seller."""
        
        if request.user.role != 'seller':
            return Response(
                {'error': 'Only sellers can access this endpoint.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Get date range from query params (default to 365 days to show all data)
        days = int(request.query_params.get('days', 365))
        start_datetime = timezone.now() - timedelta(days=days)
        
        products = Product.objects.filter(seller=request.user)
        product_ids = list(products.values_list('id', flat=True))
        
        order_items = OrderItem.objects.filter(
            product_id__in=product_ids,
            order__created_at__gte=start_datetime
        )
        
        # Sales by category
        sales_by_category = order_items.values(
            'product__category__name'
        ).annotate(
            revenue=Sum(F('price') * F('quantity')),
            units_sold=Sum('quantity')
        ).order_by('-revenue')
        
        # Product performance
        product_performance = order_items.values(
            'product_id',
            'product_name',
            'product__price'
        ).annotate(
            units_sold=Sum('quantity'),
            revenue=Sum(F('price') * F('quantity'))
        ).order_by('-revenue')
        
        # Customer insights
        unique_customers = Order.objects.filter(
            id__in=order_items.values_list('order_id', flat=True)
        ).values('user').distinct().count()
        
        repeat_customers = Order.objects.filter(
            id__in=order_items.values_list('order_id', flat=True)
        ).values('user').annotate(
            order_count=Count('id')
        ).filter(order_count__gt=1).count()
        
        return Response({
            'date_range': f'Last {days} days',
            'sales_by_category': list(sales_by_category),
            'product_performance': list(product_performance),
            'customer_insights': {
                'unique_customers': unique_customers,
                'repeat_customers': repeat_customers,
                'repeat_rate': (repeat_customers / unique_customers * 100) if unique_customers > 0 else 0
            }
        })
    
    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def orders(self, request):
        """Get orders for seller's products."""
        
        if request.user.role != 'seller':
            return Response(
                {'error': 'Only sellers can access this endpoint.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        products = Product.objects.filter(seller=request.user)
        product_ids = list(products.values_list('id', flat=True))
        
        order_items = OrderItem.objects.filter(product_id__in=product_ids)
        order_ids = order_items.values_list('order_id', flat=True).distinct()
        
        # Get status filter
        status_filter = request.query_params.get('status', None)
        orders = Order.objects.filter(id__in=order_ids)
        
        if status_filter:
            orders = orders.filter(status=status_filter)
        
        orders = orders.order_by('-created_at')
        
        # Build response
        orders_data = []
        for order in orders:
            seller_items = order_items.filter(order=order)
            order_total = seller_items.aggregate(
                total=Sum(F('price') * F('quantity'))
            )['total'] or 0
            
            orders_data.append({
                'id': order.id,
                'order_number': order.order_number,
                'status': order.status,
                'customer': {
                    'name': f"{order.user.first_name} {order.user.last_name}".strip() or order.user.username,
                    'email': order.user.email,
                },
                'shipping_address': {
                    'address': order.shipping_address,
                    'city': order.shipping_city,
                    'state': order.shipping_state,
                    'zip': order.shipping_zip,
                    'country': order.shipping_country,
                },
                'phone': order.phone,
                'items': [
                    {
                        'product_name': item.product_name,
                        'quantity': item.quantity,
                        'price': float(item.price),
                        'total': float(item.price * item.quantity)
                    }
                    for item in seller_items
                ],
                'total': float(order_total),
                'created_at': order.created_at,
                'updated_at': order.updated_at,
            })
        
        return Response({
            'count': len(orders_data),
            'results': orders_data
        })


class SellerOrderViewSet(viewsets.ViewSet):
    """ViewSet for individual seller order operations."""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def retrieve(self, request, pk=None):
        """Get a single order for the seller."""
        
        if request.user.role != 'seller':
            return Response(
                {'error': 'Only sellers can access this endpoint.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            order_id = int(pk)
        except (ValueError, TypeError):
            return Response(
                {'error': 'Invalid order ID.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get seller's products
        products = Product.objects.filter(seller=request.user)
        product_ids = list(products.values_list('id', flat=True))
        
        if not product_ids:
            return Response(
                {'error': 'No products found for this seller.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Get order items for this seller's products
        order_items = OrderItem.objects.filter(product_id__in=product_ids)
        order_ids = order_items.values_list('order_id', flat=True).distinct()
        
        # Get the specific order if it contains seller's products
        try:
            order = Order.objects.get(id=order_id, id__in=order_ids)
        except Order.DoesNotExist:
            return Response(
                {'error': 'Order not found or does not contain your products.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Get seller's items in this order
        seller_items = order_items.filter(order=order)
        
        # Build response
        order_data = {
            'id': order.id,
            'order_number': order.order_number,
            'status': order.status,
            'customer': {
                'name': f"{order.user.first_name} {order.user.last_name}".strip() or order.user.username,
                'email': order.user.email,
            },
            'shipping_address': {
                'address': order.shipping_address,
                'city': order.shipping_city,
                'state': order.shipping_state,
                'zip': order.shipping_zip,
                'country': order.shipping_country,
            },
            'phone': order.phone,
            'items': [
                {
                    'product_name': item.product_name,
                    'quantity': item.quantity,
                    'price': float(item.price),
                    'total': float(item.price * item.quantity)
                }
                for item in seller_items
            ],
            'total': float(seller_items.aggregate(
                total=Sum(F('price') * F('quantity'))
            )['total'] or 0),
            'created_at': order.created_at,
            'updated_at': order.updated_at,
        }
        
        return Response(order_data)
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def cancel_and_refund(self, request, pk=None):
        """Cancel seller's portion of an order and refund to buyer's wallet."""
        
        if request.user.role != 'seller':
            return Response(
                {'error': 'Only sellers can cancel orders.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            order_id = int(pk)
        except (ValueError, TypeError):
            return Response(
                {'error': 'Invalid order ID.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get seller's products
        products = Product.objects.filter(seller=request.user)
        product_ids = list(products.values_list('id', flat=True))
        
        if not product_ids:
            return Response(
                {'error': 'No products found for this seller.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Get order items for this seller's products
        order_items = OrderItem.objects.filter(product_id__in=product_ids)
        order_ids = order_items.values_list('order_id', flat=True).distinct()
        
        # Get the specific order if it contains seller's products
        try:
            order = Order.objects.get(id=order_id, id__in=order_ids)
        except Order.DoesNotExist:
            return Response(
                {'error': 'Order not found or does not contain your products.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check if order can be cancelled
        if order.status in ['cancelled', 'refunded', 'delivered']:
            return Response(
                {'error': f'Cannot cancel order with status: {order.status}.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get seller's items in this order (not already refunded)
        seller_items = order_items.filter(order=order, is_refunded=False)
        
        if not seller_items.exists():
            return Response(
                {'error': 'No items to refund in this order.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Calculate refund amount
        refund_amount = Decimal('0.00')
        for item in seller_items:
            refund_amount += item.price * item.quantity
        
        # Get buyer
        buyer = order.user
        
        # Restore stock for cancelled items
        for item in seller_items:
            if item.product:
                item.product.stock += item.quantity
                item.product.save()
        
        # Mark items as refunded
        now = timezone.now()
        for item in seller_items:
            item.is_refunded = True
            item.refunded_at = now
            item.save()
        
        # Add refund amount to buyer's wallet
        buyer.wallet_balance += refund_amount
        buyer.save()
        
        # Create refund record
        refund = Refund.objects.create(
            order=order,
            seller=request.user,
            amount=refund_amount,
            status='processed',
            reason=request.data.get('reason', 'Order cancelled by seller'),
            notes=request.data.get('notes', ''),
            processed_at=now
        )
        
        # Create status history
        OrderStatusHistory.objects.create(
            order=order,
            status='refunded',
            notes=f'Partially refunded by seller. Amount: ${refund_amount}',
            changed_by=request.user
        )
        
        # If all items in the order are refunded, mark order as refunded
        remaining_items = OrderItem.objects.filter(order=order, is_refunded=False)
        if not remaining_items.exists():
            order.status = 'refunded'
            order.save()
        
        return Response({
            'success': True,
            'message': f'Order items cancelled and ${refund_amount} refunded to buyer wallet.',
            'refund_amount': float(refund_amount),
            'buyer_wallet_balance': float(buyer.wallet_balance),
        })


class SellerPayoutViewSet(viewsets.ModelViewSet):
    """ViewSet for Seller Payout operations."""
    
    queryset = SellerPayout.objects.all()
    serializer_class = SellerPayoutSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        if self.request.user.role == 'seller':
            return self.queryset.filter(seller=self.request.user)
        return self.queryset.none()
    
    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def request_payout(self, request):
        """Request a payout for the seller."""
        if request.user.role != 'seller':
            return Response(
                {'error': 'Only sellers can request payouts.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            seller_profile = SellerProfile.objects.get(user=request.user)
        except SellerProfile.DoesNotExist:
            return Response(
                {'error': 'Seller profile not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Get the requested amount
        requested_amount = request.data.get('amount')
        payout_type = request.data.get('type', 'full')  # full or partial
        
        if not requested_amount:
            return Response(
                {'error': 'Amount is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            requested_amount = float(requested_amount)
        except (ValueError, TypeError):
            return Response(
                {'error': 'Invalid amount.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Calculate available balance
        products = Product.objects.filter(seller=request.user)
        product_ids = list(products.values_list('id', flat=True))
        
        order_items = OrderItem.objects.filter(product_id__in=product_ids)
        order_ids = order_items.values_list('order_id', flat=True).distinct()
        orders = Order.objects.filter(id__in=order_ids)
        
        # Calculate total revenue
        total_revenue = order_items.aggregate(
            total=Sum(F('price') * F('quantity'))
        )['total'] or 0
        
        # Get existing payouts
        pending_payout = SellerPayout.objects.filter(
            seller=request.user,
            status__in=['pending', 'processing']
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        total_payouts = SellerPayout.objects.filter(
            seller=request.user,
            status='completed'
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        available_balance = max(0, float(total_revenue) - float(pending_payout) - float(total_payouts))
        
        # Validate request
        if requested_amount <= 0:
            return Response(
                {'error': 'Amount must be greater than 0.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if requested_amount > available_balance:
            return Response(
                {'error': f'Requested amount exceeds available balance of ${available_balance:.2f}.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create payout request
        payout = SellerPayout.objects.create(
            seller=request.user,
            amount=requested_amount,
            status='pending',
            period_start=timezone.now().date() - timedelta(days=365),
            period_end=timezone.now().date(),
            notes=request.data.get('notes', '')
        )
        
        # Serialize and return
        serializer = self.get_serializer(payout)
        return Response(serializer.data, status=status.HTTP_201_CREATED)