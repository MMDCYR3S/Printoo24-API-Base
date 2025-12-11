from rest_framework import serializers
from core.models import Order, OrderStatus

class OrderStatusSerializer(serializers.ModelSerializer):
    """ نمایش خلاصه وضعیت برای لیست (با جزئیات گروه) """
    # ===== افزودن فیلدهای گروه وضعیت ===== #
    group_name = serializers.CharField(source='group.name', read_only=True)
    group_code = serializers.CharField(source='group.code', read_only=True)

    class Meta:
        model = OrderStatus
        fields = ['name', 'internal_code', 'group_name', 'group_code']
        
class OrderListSerializer(serializers.ModelSerializer):
    """
    سریالایزر لیست سفارشات برای پنل ادمین.
    """
    # ===== اطلاعات مشتری (با متد امن‌تر) ===== #
    customer_name = serializers.SerializerMethodField()
    customer_company = serializers.SerializerMethodField()
    
    # ===== وضعیت کل سفارش ===== #
    current_status = OrderStatusSerializer(read_only=True)
    
    # ===== وظایف کارمند (جدید و حیاتی) ===== #
    my_tasks_count = serializers.SerializerMethodField(
        help_text="تعداد آیتم‌هایی در این سفارش که در محدوده کاری کاربر جاری قرار دارند (و نیاز به توجه دارند)."
    )

    class Meta:
        model = Order
        fields = [
            'id', 
            'order_code', 
            'created_at', 
            'customer_name', 
            'customer_company',
            'total_price', 
            'current_status', 
            'items_count', 
            'is_locked',
            'my_tasks_count',
        ]
        read_only_fields = ['items_count', 'is_locked']

    # ========== Method Fields ========== #
    def get_customer_name(self, obj: Order):
        if hasattr(obj.user, 'customer_profile') and obj.user.customer_profile:
            profile = obj.user.customer_profile
            full_name = f"{profile.first_name} {profile.last_name}".strip()
            if full_name:
                return full_name
        return obj.user.username

    def get_customer_company(self, obj: Order):
        """ نام شرکت مشتری """
        if hasattr(obj.user, 'customer_profile') and obj.user.customer_profile:
            return obj.user.customer_profile.company or ''
        return ''
        
    def get_my_tasks_count(self, obj: Order):
        """
        محاسبه تعداد وظایف مرتبط با کاربر جاری (تعداد آیتم‌هایی که در حال حاضر در اسکوپ کاری کاربر هستند).
        
        🚨 نکته عملکردی: این فیلد باید توسط Annotation در OrderListAppService محاسبه و به آبجکت Order اضافه شود.
        اگر این کار انجام شده باشد، ما از فیلد Annotation استفاده می‌کنیم تا از N+1 Query جلوگیری شود.
        """
        # حالت بهینه: استفاده از Annotation (فرض می‌کنیم در AppService فیلدی به نام 'my_tasks_count_annotated' اضافه شده)
        if hasattr(obj, 'my_tasks_count_annotated'):
             return obj.my_tasks_count_annotated
             
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return 0
        
        count = sum(1 for item in obj.order_item_order.all() if item.assigned_to_id == request.user.id)
        return count
