from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from django.db import models
from django.db.models import Prefetch, Count, Sum, Avg
from django.db.models.functions import TruncDay
from django.utils import timezone

# ========== ORDER QUERYSET ========== #
class OrderQuerySet(models.QuerySet):
    """
    کوئری‌های پیشرفته سفارشات (گزارش‌گیری، داشبورد، دسترسی)
    """

    # ===== Access Control ===== #
    def filter_by_access(self, user):
        """
        فیلتر سفارشات براساس نقش کاربر.
        """
        if user.is_superuser:
            return self

        if not hasattr(user, 'user_role'):
            return self.none()

        role = user.user_role.role
        return self.filter(current_status__group__code=role.slug)

    # ===== Detail Views ===== #
    def get_user_orders_summary(self, user):
        """فقط خلاصه سفارشات یک کاربر"""
        return self.filter(user=user)\
            .select_related('current_status')\
            .order_by('-created_at')

    def get_order_by_id(self, order_id: int):
        """
        دریافت یک سفارش با شناسه.
        """
        return self.filter(id=order_id).first()

    def get_order_with_items(self, user_id: int, order_id: int):
        """
        دریافت جزئیات کامل سفارش برای کاربر نهایی.
        """
        # ===== دریافت ایمپورت ها===== #
        from ..models import OrderItem, OrderItemFile
        
        files_prefetch = Prefetch(
            'files',
            queryset=OrderItemFile.objects.filter(is_latest=True)
        )
        
        items_prefetch = Prefetch(
            'order_item_order',
            queryset=OrderItem.objects.select_related('product').prefetch_related(files_prefetch)
        )
        
        return self.filter(id=order_id, user_id=user_id)\
            .select_related('current_status', 'address')\
            .prefetch_related(items_prefetch)\
            .first()

    def get_all_orders_summary(self):
        return self.select_related('user', 'current_status').order_by('-created_at')

    # ===== Stats / Dashboard Methods ===== #
    def get_count_by_date_range(self, start_date: datetime, end_date: datetime) -> int:
        return self.filter(created_at__range=(start_date, end_date)).count()

    def get_pending_initial_count(self, status_code: str = 'PENDING_INITIAL_ADMIN') -> int:
        return self.filter(current_status__internal_code=status_code).count()

    def get_status_breakdown(self) -> List[Dict[str, Any]]:
        return self.values('current_status__name') \
            .annotate(count=Count('id')) \
            .order_by('-count')

    def get_total_revenue(self) -> int:
        result = self.aggregate(total=Sum('total_price'))
        return result['total'] or 0

    def get_revenue_by_date_range(self, start_date, end_date) -> int:
        result = self.filter(created_at__range=(start_date, end_date)).aggregate(total=Sum('total_price'))
        return result['total'] or 0

    def get_average_order_value(self) -> int:
        result = self.aggregate(avg=Avg('total_price'))
        return int(result['avg'] or 0)

    def get_daily_revenue_chart_data(self, days: int = 30) -> List[Dict[str, Any]]:
        start_date = timezone.now() - timedelta(days=days)
        chart_data = self.filter(created_at__gte=start_date) \
            .annotate(date=TruncDay('created_at')) \
            .values('date') \
            .annotate(total=Sum('total_price'), count=Count('id')) \
            .order_by('date')
        return list(chart_data)

    def get_top_customers_by_revenue(self, limit: int = 5):
        return self.values('user__username', 'user__customer_profile__last_name') \
            .annotate(total_spent=Sum('total_price')) \
            .order_by('-total_spent')[:limit]

# ========== ORDER MANAGER ========== #
class OrderManager(models.Manager):
    def get_queryset(self):
        return OrderQuerySet(self.model, using=self._db)
    
    def get_order_by_id(self, order_id):
        return self.get_queryset().get_order_by_id(order_id)

    # ===== Proxy Methods ===== #
    def filter_by_access(self, user):
        return self.get_queryset().filter_by_access(user)

    def get_user_orders_summary(self, user):
        return self.get_queryset().get_user_orders_summary(user)

    def get_order_with_items(self, user_id, order_id):
        return self.get_queryset().get_order_with_items(user_id, order_id)

    def get_full_order_detail_for_admin(self, order_id):
        return self.get_queryset().get_full_order_detail_for_admin(order_id)

    def get_all_orders_summary(self):
        return self.get_queryset().get_all_orders_summary()

    # ===== Stats Proxies ===== #
    def get_total_count(self):
        return self.count()

    def get_count_by_date_range(self, start, end):
        return self.get_queryset().get_count_by_date_range(start, end)

    def get_pending_initial_count(self, status_code='PENDING_INITIAL_ADMIN'):
        return self.get_queryset().get_pending_initial_count(status_code)

    def get_status_breakdown(self):
        return self.get_queryset().get_status_breakdown()

    def get_total_revenue(self):
        return self.get_queryset().get_total_revenue()

    def get_revenue_by_date_range(self, start, end):
        return self.get_queryset().get_revenue_by_date_range(start, end)

    def get_average_order_value(self):
        return self.get_queryset().get_average_order_value()

    def get_daily_revenue_chart_data(self, days=30):
        return self.get_queryset().get_daily_revenue_chart_data(days)

    def get_top_customers_by_revenue(self, limit=5):
        return self.get_queryset().get_top_customers_by_revenue(limit)

    # ===== Create Logic (from Repo) ===== #
    def create_order(self, user, current_status, address, total_price, order_type, order_code, base_price):
        return self.create(
            user=user,
            current_status=current_status,
            address=address,
            total_price=total_price,
            base_products_price=base_price,
            type=order_type,
            order_code=order_code
        )
