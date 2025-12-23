from rest_framework import serializers
from core.models import Option, OptionValue, GuideType

# ===== Option Value Serializer ===== #
class OptionValueSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    
    guide_text = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    guide_type = serializers.ChoiceField(choices=GuideType.choices, required=False, default=GuideType.INFO)

    class Meta:
        model = OptionValue
        fields = ['id', 'label', 'value', 'guide_text', 'guide_type']

# ===== Option Serializer (Nested) ===== #
class OptionSerializer(serializers.ModelSerializer):
    # ===== فیلد های مقادیر ===== #
    values = OptionValueSerializer(source='global_values', many=True, required=False)
    
    # فیلدهای راهنما برای خودِ ویژگی
    guide_text = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    guide_type = serializers.ChoiceField(choices=GuideType.choices, required=False, default=GuideType.INFO)

    class Meta:
        model = Option
        fields = [
            'id', 'name', 'label', 'input_type', 
            'values', 'guide_text', 'guide_type', 
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']
        
    def validate(self, data):
        return data
