from rest_framework import serializers
from core.models import User, Role
from django.contrib.auth.models import Permission

# ========== Permission & Role DTOs ========== #
class PermissionSerializer(serializers.ModelSerializer):
    """ نمایش لیست دسترسی‌های موجود در سیستم """
    class Meta:
        model = Permission
        fields = ['id', 'name', 'codename', 'content_type']

class RoleOutputSerializer(serializers.ModelSerializer):
    """ فرمت خروجی نقش برای نمایش در لیست """
    permission = PermissionSerializer(many=True, read_only=True)
    
    class Meta:
        model = Role
        fields = ['id', 'name', 'slug', 'description', 'is_customer', 'permission']

class RoleInputSerializer(serializers.Serializer):
    """ فرمت ورودی برای ساخت/ویرایش نقش """
    name = serializers.CharField(max_length=150)
    slug = serializers.CharField(max_length=50)
    description = serializers.CharField(required=False, allow_blank=True)
    permissions = serializers.ListField(
        child=serializers.IntegerField(), required=False, allow_empty=True
    )


# ========== Staff User DTOs ========== #
class StaffListSerializer(serializers.ModelSerializer):
    """ لیست کارکنان برای نمایش در جدول """
    role_name = serializers.CharField(source='user_role.first.role.name', read_only=True)
    role_id = serializers.IntegerField(source='user_role.first.role.id', read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'is_active', 'last_login', 'role_name', 'role_id']

class StaffCreateSerializer(serializers.Serializer):
    """ فرم استخدام کارمند جدید """
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8)
    role_id = serializers.IntegerField()

class StaffUpdateSerializer(serializers.Serializer):
    """ فرم ویرایش کارمند """
    email = serializers.EmailField(required=False)
    role_id = serializers.IntegerField(required=False)
    is_active = serializers.BooleanField(required=False)

# ========== Bulk Action DTOs ========== #
class BulkIdsSerializer(serializers.Serializer):
    """ ورودی ساده برای عملیات گروهی (فقط لیست ID) """
    ids = serializers.ListField(child=serializers.IntegerField(), allow_empty=False)

class BulkRoleChangeSerializer(serializers.Serializer):
    """ ورودی برای تغییر نقش گروهی """
    ids = serializers.ListField(child=serializers.IntegerField(), allow_empty=False)
    new_role_id = serializers.IntegerField()
    
# ========== Authentication DTOs ========== #
class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

class RefreshTokenSerializer(serializers.Serializer):
    refresh = serializers.CharField()