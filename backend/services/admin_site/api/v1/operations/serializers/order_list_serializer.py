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
            'is_locked'
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
