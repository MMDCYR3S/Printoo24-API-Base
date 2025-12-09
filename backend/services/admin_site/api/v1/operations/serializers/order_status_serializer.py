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