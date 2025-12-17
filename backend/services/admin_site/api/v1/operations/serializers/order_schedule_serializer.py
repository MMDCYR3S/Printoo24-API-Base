from rest_framework import serializers
from core.models import OrderSchedule

# ========== SCHEDULE SERIALIZERS ========== #
class OrderScheduleSerializer(serializers.ModelSerializer):
    """
    سریالایزر زمان‌بندی سفارش.
    """
    duration_days = serializers.IntegerField(read_only=True)
    remaining_days = serializers.IntegerField(read_only=True)
    is_overdue = serializers.BooleanField(read_only=True)
    delay_days = serializers.IntegerField(read_only=True)

    class Meta:
        model = OrderSchedule
        fields = [
            'id', 
            'start_date', 
            'due_date', 
            'completed_at', 
            'duration_days',
            'remaining_days',
            'is_overdue',
            'delay_days',
            'created_at',
            'updated_at'
        ]

    def validate(self, data):
        """ اعتبارسنجی منطقی تاریخ‌ها """
        start = data.get('start_date')
        due = data.get('due_date')
        
        if self.instance:
            start = start or self.instance.start_date
            due = due or self.instance.due_date

        if start and due and due < start:
            raise serializers.ValidationError({"due_date": "تاریخ تحویل نمی‌تواند قبل از تاریخ شروع باشد."})
            
        return data
