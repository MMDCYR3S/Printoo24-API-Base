from rest_framework import serializers
from core.models import User, Role

# ===== Role Minimal ===== #
class RoleMinimalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ['id', 'name', 'slug']

# ===== Staff List & Detail ===== #
class StaffSerializer(serializers.ModelSerializer):
    role = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'is_active', 
            'is_staff', 'is_superuser', 'created_at', 'role'
        ]

    def get_role(self, obj):
        # ===== استخراج نقش کارمند از جدول واسط ===== #
        user_role = obj.user_role.first()
        if user_role and user_role.role:
            return RoleMinimalSerializer(user_role.role).data
        return None

# ===== Create Staff Input ===== #
class StaffCreateSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=150, required=True)
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    role_id = serializers.IntegerField(required=True, help_text="شناسه نقش کارمند")

# ===== Update Staff Input ===== #
class StaffUpdateSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=150, required=False)
    password = serializers.CharField(write_only=True, required=False, style={'input_type': 'password'})
    role_id = serializers.IntegerField(required=False, help_text="شناسه نقش جدید")
    is_active = serializers.BooleanField(required=False)

# ===== Bulk Actions Inputs ===== #
class BulkIdsSerializer(serializers.Serializer):
    user_ids = serializers.ListField(
        child=serializers.IntegerField(), 
        required=True, 
        allow_empty=False
    )

class BulkToggleStatusSerializer(BulkIdsSerializer):
    is_active = serializers.BooleanField(required=True)

class BulkChangeRoleSerializer(BulkIdsSerializer):
    role_id = serializers.IntegerField(required=True)

# ========== Role DTOs ========== #
class RoleSerializer(serializers.ModelSerializer):
    """ خروجی نقش به همراه تعداد دسترسی‌ها و اسکوپ‌ها """
    class Meta:
        model = Role
        fields = ['id', 'name', 'slug']
    
