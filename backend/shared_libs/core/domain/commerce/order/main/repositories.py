from typing import List, Optional, Any, Dict
from datetime import datetime, timedelta

from django.utils import timezone
from django.db.models import Prefetch, QuerySet, Count, Sum, Avg
from django.db.models.functions import TruncDay

from core.utils.base_repository import BaseRepository
from core.models import (
    Order, OrderItem, OrderItemFile, OrderStatus, Address, User,
    OrderCostItem, OrderShipment, OrderCostSheet, 
    OrderPrintReport, OrderPrintItem, OrderCostReport
)

class OrderRepository(BaseRepository[Order]):
    def __init__(self):
        super().__init__(Order)
    
    # ===== منطق سمت مشتری ===== #
    def get_order_by_id(self, order_id: int) -> Optional[Order]:
        return self.get_by_id(order_id)
    
    def get_order_by_user(self, user: User) -> List[Order]:
        return self.filter(user=user)
    
    def get_user_orders_summary(self, user: User) -> QuerySet[Order]:
        """فقط خلاصه سفارشات"""
        return self.model.objects.filter(user=user)\
            .select_related('current_status')\
            .order_by('-created_at')
    
    def create_order(self, user: User, order_status: OrderStatus, address: Address, 
                     total_price: float, order_type: str, order_code: str, base_price: float) -> Order: 
        return self.create({
            "user": user,
            "current_status": order_status,
            "address": address,
            "total_price": total_price,
            "base_products_price": base_price,
            "type": order_type,
            "order_code": order_code
        })
    
    def get_order_with_items(self, user_id: int, order_id: int) -> Optional[Order]:
        """
        دریافت جزئیات کامل سفارش برای کاربر نهایی.
        """
        files_prefetch = Prefetch(
            'files',
            queryset=OrderItemFile.objects.filter(is_latest=True).select_related('requirement__spec')
        )
        
        items_prefetch = Prefetch(
            'order_item_order',
            queryset=OrderItem.objects.select_related('product').prefetch_related(files_prefetch)
        )
        
        return self.model.objects.filter(id=order_id, user_id=user_id)\
            .select_related('current_status', 'address')\
            .prefetch_related(items_prefetch)\
            .first()
    
    # ===== سمت ادمین - بخش مدیریت داخلی ===== #
    def get_full_order_detail_for_admin(self, order_id: int) -> Optional[Order]:
        """
        دریافت سوپر-دیتا برای پنل مدیریت.
        ساختار جدید مالی: Order -> CostSheet -> CostReports -> CostItems
        """
        return self.model.objects.select_related(
            'user', 
            'current_status__group', 
            'address__city',
            'address__province', 
            'related_invoice'
        ).prefetch_related(
            # 1. آیتم‌ها و فایل‌ها
            Prefetch(
                'order_item_order',
                queryset=OrderItem.objects.select_related('product').prefetch_related(
                    Prefetch(
                        'files', 
                        queryset=OrderItemFile.objects.filter(is_latest=True).select_related('requirement__spec').order_by('-version')
                    )
                )
            ),
            
            # 3. ساختار مالی جدید (Sheet -> Reports -> Items)
            Prefetch(
                'cost_sheet',
                queryset=OrderCostSheet.objects.prefetch_related(
                    Prefetch(
                        'reports',
                        queryset=OrderCostReport.objects.select_related('submitter').prefetch_related(
                            Prefetch(
                                'items',
                                queryset=OrderCostItem.objects.select_related('catalog_item')
                            ),
                            'attachments'
                        ).order_by('-created_at')
                    )
                )
            ),

            # 4. گزارشات چاپ
            Prefetch(
                'print_reports',
                    queryset=OrderPrintReport.objects.select_related('created_by').prefetch_related(
                        Prefetch(
                            'items',
                            queryset=OrderPrintItem.objects.select_related('material_type')
                        ),
                        'attachments'
                    )
            ),
            
            # 5. مرسولات
            Prefetch(
                'shipments', 
                queryset=OrderShipment.objects.select_related('delivery_method', 'destination_address').prefetch_related('packages')
            )
        ).filter(id=order_id).first()
        
    def get_all_orders_summary(self) -> QuerySet[Order]:
        return self.model.objects.select_related(
            'user', 'current_status'
        ).order_by('-created_at')
        
    # ======== Dashboard / Stats Methods ======= #
    def get_total_count(self) -> int:
        """دریافت تعداد کل سفارشات ثبت شده"""
        return self.model.objects.count()

    def get_count_by_date_range(self, start_date: datetime, end_date: datetime) -> int:
        """
        تعداد سفارشات در یک بازه زمانی خاص.
        کاربرد: محاسبه تعداد سفارشات ماه جاری و ماه قبل.
        """
        return self.model.objects.filter(created_at__range=(start_date, end_date)).count()

    def get_pending_initial_count(self, status_code: str = 'PENDING_INITIAL_ADMIN') -> int:
        """
        تعداد سفارشاتی که در وضعیت 'در انتظار تایید اولیه' هستند.
        """
        return self.model.objects.filter(current_status__internal_code=status_code).count()

    def get_status_breakdown(self) -> List[Dict[str, Any]]:
        """
        تفکیک سفارشات بر اساس وضعیت.
        خروجی: لیستی از دیکشنری‌ها شامل نام وضعیت و تعداد.
        Example: [{'current_status__name': 'تکمیل شده', 'count': 50}, ...]
        """
        return self.model.objects.values('current_status__name') \
            .annotate(count=Count('id')) \
            .order_by('-count')

    # ========== Dashboard / Financial Chart ========== #
    def get_total_revenue(self) -> int:
        """جمع کل مبلغ سفارشات (درآمد کل)"""
        result = self.model.objects.aggregate(total=Sum('total_price'))
        return result['total'] or 0

    def get_revenue_by_date_range(self, start_date, end_date) -> int:
        """درآمد در یک بازه زمانی خاص"""
        result = self.model.objects.filter(
            created_at__range=(start_date, end_date)
        ).aggregate(total=Sum('total_price'))
        return result['total'] or 0

    def get_average_order_value(self) -> int:
        """میانگین ارزش سبد خرید (AOV)"""
        result = self.model.objects.aggregate(avg=Avg('total_price'))
        return int(result['avg'] or 0)

    def get_daily_revenue_chart_data(self, days: int = 30) -> List[Dict[str, Any]]:
        """
        دریافت داده‌های نموداری: فروش روزانه در N روز گذشته.
        خروجی: لیستی از دیکشنری‌ها {date: '2023-10-01', total: 5000000}
        """
        start_date = timezone.now() - timedelta(days=days)
        
        chart_data = self.model.objects.filter(created_at__gte=start_date) \
            .annotate(date=TruncDay('created_at')) \
            .values('date') \
            .annotate(total=Sum('total_price'), count=Count('id')) \
            .order_by('date')
            
        return list(chart_data)

    def get_top_customers_by_revenue(self, limit: int = 5) -> QuerySet:
        """(اختیاری) برترین مشتریان بر اساس پول خرج شده"""
        return self.model.objects.values('user__username', 'user__customer_profile__last_name') \
            .annotate(total_spent=Sum('total_price')) \
            .order_by('-total_spent')[:limit]

# ======= Order Item Repositories ======= #
class OrderItemRepository(BaseRepository[OrderItem]):
    def __init__(self):
        super().__init__(OrderItem)

class OrderItemFileRepository(BaseRepository[OrderItemFile]):
    def __init__(self):
        super().__init__(OrderItemFile)
