from rest_framework import serializers
from core.models import OrderStatusGroup, OrderStatus

class OrderStatusGroupMinimalSerializer(serializers.ModelSerializer):
    """ نمایش مختصر گروه وضعیت """
    class Meta:
        model = OrderStatusGroup
        fields = ['id', 'name', 'code']

class OrderStatusListSerializer(serializers.ModelSerializer):
    """ سریالایزر نمایش وضعیت‌های سفارش. """
    group = OrderStatusGroupMinimalSerializer(read_only=True)

    class Meta:
        model = OrderStatus
        fields = ['id', 'name', 'internal_code', 'group', 'description', 'created_at']

class OrderStatusInputSerializer(serializers.ModelSerializer):
    """ سریالایزر ورودی برای ایجاد و ویرایش وضعیت سفارش. """
    group_id = serializers.PrimaryKeyRelatedField(
        queryset=OrderStatusGroup.objects.all(), source='group', write_only=True
    )
    
    class Meta:
        model = OrderStatus
        fields = ['name', 'internal_code', 'description', 'group_id']
        
class OrderTransitionSerializer(serializers.Serializer):
    """ 
    ورودی تغییر وضعیت سفارش (Simplified).
    فقط کد وضعیت جدید و توضیحات دریافت می‌شود.
    """
    new_status_code = serializers.CharField(
        required=True, 
        help_text="کد سیستمی وضعیت جدید (مثلاً: DESIGN_APPROVED)"
    )
    description = serializers.CharField(
        required=False, 
        allow_blank=True,
        help_text="توضیحات اختیاری (دلیل رد یا تایید)"
    )
    
    def validate_new_status_code(self, value):
        """ نرمال‌سازی کد وضعیت به حروف بزرگ """
        return value.upper().strip()
        