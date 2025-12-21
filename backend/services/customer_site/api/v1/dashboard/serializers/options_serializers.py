from rest_framework import serializers
from core.models import Option, OptionValue

# ===== Option Value Serializer ===== #
class OptionValueSerializer(serializers.ModelSerializer):
    class Meta:
        model = OptionValue
        fields = ['id', 'label', 'value']
        read_only_fields = ['id']

# ===== Option Serializer (Nested) ===== #
class OptionSerializer(serializers.ModelSerializer):
    # ===== فیلد های مقادیر ===== #
    values = OptionValueSerializer(source='global_values', many=True, required=False)

    class Meta:
        model = Option
        fields = ['id', 'name', 'label', 'values', 'created_at']
        read_only_fields = ['id', 'created_at']
        
    def validate(self, data):
        """
        اعتبارسنجی سطح سریالایزر برای اطمینان از فرمت صحیح.
        """
        return data