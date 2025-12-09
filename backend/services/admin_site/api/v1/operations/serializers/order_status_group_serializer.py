from rest_framework import serializers
from core.models import OrderStatusGroup

# ========== Order Status Group Serializers ========== #
class OrderStatusGroupListSerializer(serializers.ModelSerializer):
    """ سریالایزر نمایش لیست و جزئیات گروه وضعیت. """
    status_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = OrderStatusGroup
        fields = ['id', 'name', 'code', 'description', 'status_count', 'created_at']
        read_only_fields = ['status_count']

class OrderStatusGroupInputSerializer(serializers.ModelSerializer):
    """ سریالایزر ورودی برای ایجاد و ویرایش گروه وضعیت. """
    class Meta:
        model = OrderStatusGroup
        fields = ['name', 'code', 'description']