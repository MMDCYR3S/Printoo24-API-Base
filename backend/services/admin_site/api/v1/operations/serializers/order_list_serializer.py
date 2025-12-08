from rest_framework import serializers
from core.models import Order

class OrderStatusSerializer(serializers.Serializer):
    """ نمایش خلاصه وضعیت برای لیست """
    name = serializers.CharField()
    internal_code = serializers.CharField()
    group = serializers.CharField()

class OrderListSerializer(serializers.ModelSerializer):
    """
    سریالایزر لیست سفارشات برای پنل ادمین.
    اطلاعات کلیدی را برای تصمیم‌گیری سریع نشان می‌دهد.
    """
    # ===== اطلاعات مشتری ===== #
    customer_name = serializers.SerializerMethodField()
    customer_company = serializers.CharField(source='user.customer_profile.company', read_only=True)
    
    # ===== وضعیت ===== #
    current_status = OrderStatusSerializer(read_only=True)
    
    # ===== اطلاعات مالی ===== #
    total_price = serializers.IntegerField()
    
    # ===== اطلاعات فرایند ===== #
    items_count = serializers.IntegerField(read_only=True)
    is_locked = serializers.BooleanField(read_only=True)
    
    # ===== بررسی اختصاص به کاربر ===== #
    is_assigned_to_me = serializers.SerializerMethodField()

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
            'is_assigned_to_me'
        ]

    def get_customer_name(self, obj):
        if hasattr(obj.user, 'customer_profile'):
            profile = obj.user.customer_profile
            full_name = f"{profile.first_name} {profile.last_name}".strip()
            if full_name:
                return full_name
        return obj.user.username

    def get_is_assigned_to_me(self, obj):
        """
        بررسی می‌کند آیا کاربر جاری (Request User) مسئول انجام آیتم‌های این سفارش است؟
        """
        request = self.context.get('request')
        if not request or not request.user:
            return False
        
        for item in obj.order_item_order.all():
            if item.assigned_to_id == request.user.id:
                return True
        return False
