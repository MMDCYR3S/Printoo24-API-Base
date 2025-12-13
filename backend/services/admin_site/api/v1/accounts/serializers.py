from rest_framework import serializers
from core.models import User, Role
from django.contrib.auth.models import Permission

# ========== Permission & Role DTOs ========== #
class PermissionSerializer(serializers.ModelSerializer):
    """ نمایش لیست دسترسی‌های موجود در سیستم """
    class Meta:
        model = Permission
        fields = ['id', 'name', 'codename', 'content_type']

# ==========================================
# ========== Role DTOs =====================
# ==========================================
class RoleOutputSerializer(serializers.ModelSerializer):
    """ خروجی نقش به همراه تعداد دسترسی‌ها و اسکوپ‌ها """
    permission_count = serializers.SerializerMethodField()
    type_display = serializers.CharField(source='get_type_display', read_only=True)
    allowed_groups = serializers.SerializerMethodField()

    class Meta:
        model = Role
        fields = ['id', 'name', 'slug', 'type', 'type_display', 'description', 'is_customer', 'permission_count', 'allowed_groups']

    def get_allowed_groups(self, obj):
        return [group.name for group in obj.allowed_groups.all()]

    def get_permission_count(self, obj):
        return obj.permission.count()
    
# ========== Role Input DTOs ========== #
class RoleInputSerializer(serializers.Serializer):
    """ 
    فرمت ورودی ایجاد/ویرایش نقش.
    """
    name = serializers.CharField(max_length=150)
    slug = serializers.CharField(max_length=50)
    description = serializers.CharField(required=False, allow_blank=True)
    
    type = serializers.ChoiceField(
        choices=Role.USER_TYPE, 
        required=True,
        help_text="نقش ادمین یا کاربر عادی"
    )
    is_customer = serializers.BooleanField(default=False)
    
    # ===== لیست مجوزها ===== #
    permissions = serializers.ListField(
        child=serializers.IntegerField(), 
        required=False, 
        allow_empty=True
    )

    # ===== لیست اسکوپ‌ها (حیاتی) ===== #
    allowed_groups_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        allow_empty=True,
        help_text="لیست شناسه (ID) گروه‌های وضعیت (Order Status Groups) که این نقش اجازه مشاهده آن‌ها را دارد."
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