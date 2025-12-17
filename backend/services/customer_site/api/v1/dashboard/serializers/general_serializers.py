from rest_framework import serializers
from core.models import (
    ProductCategory,
    ContactUs,
    PromotionalModal,
    User,
    Wallet,
    WalletTransaction
)

# ===== سریالایزر مدیریت دسته‌بندی‌ها (داشبورد) ===== #
class ProductCategoryDashboardSerializer(serializers.ModelSerializer):
    banner_wide_url = serializers.CharField(source='get_banner_wide_url', read_only=True)
    
    class Meta:
        model = ProductCategory
        fields = [
            'id', 'name', 'slug', 'parent', 'description',
            'banner_wide', 'banner_box', 'banner_wide_url',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'slug', 'created_at', 'updated_at', 'banner_wide_url']

# ===== سریالایزر تماس با ما ===== #
class ContactUsSerializer(serializers.ModelSerializer):
    """
    این سریالایزر برای اعتبارسنجی و نمایش فرم تماس با ما است.
    """
    class Meta:
        model = ContactUs
        fields = ['id', 'full_name', 'email', 'phone_number', 'subject', 'message', 'created_at']
        read_only_fields = ['id', 'created_at', 'is_read'] # کاربر نباید بتواند تیک خوانده شده را بزند!


# ===== سریالایزر مودال تبلیغاتی ===== #
class PromotionalModalSerializer(serializers.ModelSerializer):
    """
    سریالایزر مودال.
    نکته سینیور: ما image_url را به صورت computed field برمی‌گردانیم
    تا فرانت‌اند درگیر مسیر فایل نشود.
    """
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = PromotionalModal
        fields = [
            'id', 'title', 'description', 'image', 'image_url',
            'cta_text', 'cta_url', 'is_active', 'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'image_url']
        
    def get_image_url(self, obj):
        if obj.image:
            # ===== اطمینان از اینکه Request در کانتکست وجود دارد ===== #
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None

# ===== سریالایزر ورودی (فقط برای دریافت متن) ===== #
class ReplyMessageSerializer(serializers.Serializer):
    reply_text = serializers.CharField(
        required=True, 
        min_length=5, 
        label="متن پاسخ",
        style={'base_template': 'textarea.html'}
    )

# ===== سریالایزر ترکیبی ===== #
class CustomerManagementSerializer(serializers.ModelSerializer):
    # ===== فیلدهای پروفایل ===== #
    first_name = serializers.CharField(source='customer_profile.first_name', required=False)
    last_name = serializers.CharField(source='customer_profile.last_name', required=False)
    phone_number = serializers.CharField(source='customer_profile.phone_number', required=False)
    company = serializers.CharField(source='customer_profile.company', required=False, allow_null=True)
    bio = serializers.CharField(source='customer_profile.bio', required=False, allow_null=True)
    
    # ===== فیلد های مربوط به کیف پول ===== #
    wallet_balance = serializers.DecimalField(
        source='wallet.decimal', 
        max_digits=12, 
        decimal_places=2, 
        read_only=True
    )

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'password', 'is_active', 'is_staff', 'is_superuser',
            'is_verified', 'first_name', 'last_name', 'phone_number', 'company', 'bio', 
            'wallet_balance', 'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'wallet_balance']
        extra_kwargs = {
            'password': {'write_only': True, 'required': False},
            'username': {'required': True},
            'email': {'required': True},
        }

# ===== سریالایزر نمایش تراکنش‌ها ===== #
class WalletTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = WalletTransaction
        fields = ['id', 'type', 'amount', 'amount_after', 'created_at']


# ===== سریالایزر نمایش کیف پول (Read) ===== #
class WalletDetailSerializer(serializers.ModelSerializer):
    # ===== نمایش اطلاعات کامل کیف پول ===== #
    user_full_name = serializers.CharField(source='user.customer_profile.full_name', read_only=True, default='-')
    username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = Wallet
        fields = ['id', 'user_id', 'username', 'user_full_name', 'decimal', 'updated_at']


# ===== سریالایزر تغییر موجودی (Action) ===== #
class WalletAdjustmentSerializer(serializers.Serializer):
    amount = serializers.DecimalField(
        max_digits=12, 
        decimal_places=0, 
        min_value=1,
        label="مبلغ"
    )
    action_type = serializers.ChoiceField(
        choices=[('deposit', 'افزایش موجودی'), ('withdraw', 'کاهش موجودی')],
        label="نوع عملیات"
    )
    description = serializers.CharField(
        required=False, 
        allow_blank=True, 
        label="توضیحات (بابت)"
    )
