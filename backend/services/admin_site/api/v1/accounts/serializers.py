from rest_framework import serializers
from core.models import User, Role, Address, Province, City
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

# ========== Role DTOs ========== #
class RoleSerializer(serializers.ModelSerializer):
    """ خروجی نقش به همراه تعداد دسترسی‌ها و اسکوپ‌ها """
    class Meta:
        model = Role
        fields = ['id', 'name', 'slug']
    
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
    """ فرم ویرایش کارمند با قابلیت تغییر رمز عبور """
    email = serializers.EmailField(required=False)
    username = serializers.CharField(max_length=150, required=False)
    role_id = serializers.IntegerField(required=False)
    is_active = serializers.BooleanField(required=False)
    password = serializers.CharField(
        write_only=True, 
        required=False, 
        min_length=8,
        help_text="در صورت نیاز به تغییر رمز عبور، مقدار ارسال شود."
    )

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


# ========== Customer Serializers ========== #
class CustomerListSerializer(serializers.ModelSerializer):
    """
    خروجی لیست مشتریان.
    اطلاعات User و Profile را ترکیب می‌کند.
    """
    first_name = serializers.CharField(source='customer_profile.first_name', read_only=True)
    last_name = serializers.CharField(source='customer_profile.last_name', read_only=True)
    phone_number = serializers.CharField(source='customer_profile.phone_number', read_only=True)
    company = serializers.CharField(source='customer_profile.company', read_only=True)
    bio = serializers.CharField(source='customer_profile.bio', read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'is_active', 'last_login', 'created_at',
            'first_name', 'last_name', 'phone_number', 'company', 'bio'
        ]

# ========== CUSTOMER UPDATE SERIALIZER ========== #
class CustomerUpdateSerializer(serializers.Serializer):
    """
    ویرایش اطلاعات مشتری.
    """
    email = serializers.EmailField(required=False)
    is_active = serializers.BooleanField(required=False)
    password = serializers.CharField(required=False, write_only=True, min_length=8)

    first_name = serializers.CharField(required=False, allow_blank=True)
    last_name = serializers.CharField(required=False, allow_blank=True)
    phone_number = serializers.CharField(required=False, allow_blank=True)
    company = serializers.CharField(required=False, allow_blank=True)
    bio = serializers.CharField(required=False, allow_blank=True)

# ========== GEO SERIALIZERS ========== #
class ProvinceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Province
        fields = ['id', 'name', 'slug']

class CitySerializer(serializers.ModelSerializer):
    province_name = serializers.CharField(source='province.name', read_only=True)
    
    class Meta:
        model = City
        fields = ['id', 'name', 'slug', 'province', 'province_name']

# ========== ADDRESS SERIALIZERS ========== #
class AddressSerializer(serializers.ModelSerializer):
    """
    سریالایزر برای نمایش و ایجاد/ویرایش آدرس
    """
    province_id = serializers.IntegerField(write_only=True)
    city_id = serializers.IntegerField(write_only=True)
    
    # ===== اطلاعات آدرس ===== #
    province = serializers.CharField(source='province.name', read_only=True)
    city = serializers.CharField(source='city.name', read_only=True)

    class Meta:
        model = Address
        fields = [
            'id', 'province_id', 'city_id', 'postal_code', 'address', 
            'province', 'city', 'created_at'
        ]

# ========== CUSTOMER SERIALIZERS ========== #
class CustomerCreateSerializer(serializers.Serializer):
    """
    آپدیت شده: اضافه شدن فیلد addresses
    """
    # ===== اطلاعات اصلی کاربر ===== #
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8)
    is_active = serializers.BooleanField(default=True)

    # ===== اطلاعات پروفایل ===== #
    first_name = serializers.CharField(max_length=150, required=False, allow_blank=True)
    last_name = serializers.CharField(max_length=150, required=False, allow_blank=True)
    phone_number = serializers.CharField(max_length=150, required=False, allow_blank=True)
    company = serializers.CharField(max_length=150, required=False, allow_blank=True)
    bio = serializers.CharField(required=False, allow_blank=True)

    # ===== اطلاعات آدرس ===== #
    addresses = AddressSerializer(many=True, required=False, write_only=True)

class CustomerDetailSerializer(serializers.ModelSerializer):
    """
    نمایش جزئیات کامل یک مشتری شامل پروفایل و تمام آدرس‌ها
    """
    # ===== اطلاعات پروفایل ===== #
    first_name = serializers.CharField(source='customer_profile.first_name', read_only=True)
    last_name = serializers.CharField(source='customer_profile.last_name', read_only=True)
    phone_number = serializers.CharField(source='customer_profile.phone_number', read_only=True)
    company = serializers.CharField(source='customer_profile.company', read_only=True)
    bio = serializers.CharField(source='customer_profile.bio', read_only=True)
    
    # ===== آدرس ===== #
    addresses = AddressSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'is_active', 'last_login', 'created_at',
            'first_name', 'last_name', 'phone_number', 'company', 'bio',
            'addresses'
        ]
