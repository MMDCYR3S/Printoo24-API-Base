from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field

from core.models import (
    ProductCategory,
    Product,
    Province,
    City,
    Address,
    User,
)
from apps.accounts.models import (
    Wallet,
    WalletTransaction,
)
from apps.home.models import ContactUs, PromotionalModal

# ========== CATEGORY SERIALIZERS ========== #
# ===== سریالایزر مینیمال محصول برای نمایش در لیست‌ها ===== #
class ProductMinimalSerializer(serializers.ModelSerializer):
    """
    سریالایزر سبک برای نمایش در لایه دسته‌بندی‌ها.
    شامل کمترین اطلاعات برای رندر کردن کارت محصول.
    """
    image_url = serializers.SerializerMethodField()
    price_display = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['id', 'name', 'slug', 'price', 'image_url', 'price_display']

    def get_image_url(self, obj):
        if hasattr(obj, 'media') and obj.media.exists():
            image = obj.media.first().file
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(image.url)
            return image.url
        
        # اگر عکس ندارد، از یک پلیس‌هولدر استفاده کن
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri('/static/images/no-image.png')
        return '/static/images/no-image.png'

    def get_price_display(self, obj):
        return f"{obj.price:,.0f}"

# ===== سریالایزر مدیریت دسته‌بندی‌ها (داشبورد) ===== #
class CategoryLinkSerializer(serializers.ModelSerializer):
    """
    نمایش نام و لینک جزئیات برای فرزندان
    """
    detail_url = serializers.HyperlinkedIdentityField(
        view_name='api:v1:dashboard:product_category_dashboard-detail',
        lookup_field='id'
    )
    products = ProductMinimalSerializer(many=True, read_only=True)

    class Meta:
        model = ProductCategory
        fields = ['id', 'name', 'detail_url', 'products']

# ======= 
class ParentCategoryListSerializer(serializers.ModelSerializer):
    """
    مخصوص لیست والدها: بدون عکس، فقط اطلاعات پایه و لینک جزئیات
    """
    detail_url = serializers.HyperlinkedIdentityField(
        view_name='api:v1:dashboard:product_category_dashboard-detail',
        lookup_field='id'
    )
    banner_wide_url = serializers.CharField(source='get_banner_wide_url', read_only=True)
    children_count = serializers.SerializerMethodField()
    products = ProductMinimalSerializer(many=True, read_only=True)

    class Meta:
        model = ProductCategory
        fields = [
            'id', 'name', 'slug', 'detail_url', 'is_active',
            'banner_wide', 'banner_box', 'banner_wide_url',
            'children_count', 'products'
        ]
        
    def get_children_count(self, obj):
        """
        محاسبه تعداد فرزندان مستقیم
        """
        return obj.get_children().count()
    
# ===== سریالایزر اطلاعات والد (Nested Serializer) ===== #
class ParentInfoSerializer(serializers.Serializer):
    """
    نمایش اطلاعات خلاصه شده والد دسته‌بندی.
    این سریالایزر برای جلوگیری از تودرتو شدن بی‌مورد و ساده کردن خروجی استفاده می‌شود.
    """
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(read_only=True)
    slug = serializers.SlugField(read_only=True)

# ===== سریالایزر لیست زیردسته‌ها ===== #
class SubcategoryWithParentSerializer(serializers.Serializer):
    """
    نمایش لیست مسطح زیردسته‌ها به همراه اطلاعات والد.
    این ساختار دقیقاً خروجی متد get_subcategories_flat_list در سرویس اپلیکیشن را پوشش می‌دهد.
    """
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(read_only=True)
    slug = serializers.SlugField(read_only=True)
    parent = ParentInfoSerializer(read_only=True)
    products = ProductMinimalSerializer(many=True, read_only=True)

# ========== جزئیات با لینک ========== #
class ProductCategoryDetailWithLinksSerializer(serializers.ModelSerializer):
    """
    نمایش جزئیات کامل + لیست فرزندان به صورت لینک
    """
    banner_wide_url = serializers.CharField(source='get_banner_wide_url', read_only=True)
    children = CategoryLinkSerializer(many=True, read_only=True, source='get_children')
    parent_name = serializers.CharField(source='parent.name', read_only=True)
    products = ProductMinimalSerializer(many=True, read_only=True)

    class Meta:
        model = ProductCategory
        fields = [
            'id', 'name', 'slug', 'parent', 'parent_name', 'description',
            'banner_wide', 'banner_box', 'banner_wide_url',
            'is_active', 'children', 'products', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'slug', 'created_at', 'updated_at', 'banner_wide_url']

class ProductCategoryDashboardSerializer(serializers.ModelSerializer):
    banner_wide_url = serializers.CharField(source='get_banner_wide_url', read_only=True)
    children = serializers.SerializerMethodField()
    parent_name = serializers.CharField(source='parent.name', read_only=True)
    
    class Meta:
        model = ProductCategory
        fields = [
            'id', 'user', 'name', 'slug', 'parent', 'parent_name', 'description',
            'banner_wide', 'banner_box', 'banner_wide_url',
            'is_active', 'children', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'slug', 'created_at', 'updated_at', 'banner_wide_url']
        
    @extend_schema_field(serializers.ListField(child=serializers.DictField()))
    def get_children(self, obj):
        """
        بازگرداندن فرزندان به صورت بازگشتی.
        اگر فرزندی وجود داشته باشد، همین سریالایزر را برای آن‌ها صدا می‌زنیم.
        """
        children = obj.get_children()
        if children.exists():
            return ProductCategoryDashboardSerializer(children, many=True, context=self.context).data
        return []

# ===== سریالایزر ورودی برای عملیات گروهی ===== #
class CategoryBulkUpsertSerializer(serializers.Serializer):
    """
    سریالایزر برای دریافت لیست دسته‌بندی‌ها جهت ایجاد یا ویرایش گروهی.
    فیلد id: اگر ارسال شود => Update. اگر خالی باشد => Create.
    فیلد parent_slug: برای اتصال به والد (چه موجود در دیتابیس چه در همین لیست).
    """
    id = serializers.IntegerField(required=False, allow_null=True)
    name = serializers.CharField(max_length=150)
    parent_slug = serializers.SlugField(max_length=150, required=False, allow_null=True, allow_blank=True, write_only=True)
    description = serializers.CharField(required=False, allow_blank=True)
    is_active = serializers.BooleanField(required=False, default=True)

# ========== OTHER SERIALIZERS ========== #
# ===== سریالایزر تماس با ما ===== #
class ContactUsSerializer(serializers.ModelSerializer):
    status_display = serializers.SerializerMethodField()
    
    class Meta:
        model = ContactUs
        fields = [
            'id', 'full_name', 'email', 'phone_number', 'subject', 'message', 
            'is_read', 'admin_reply', 'replied_at', 'created_at', 'status_display'
        ]
        read_only_fields = ['is_read', 'admin_reply', 'replied_at', 'created_at']

    def get_status_display(self, obj):
        if obj.admin_reply:
            return "پاسخ داده شده"
        if obj.is_read:
            return "خوانده شده (بدون پاسخ)"
        return "جدید"


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

class AddressSerializer(serializers.ModelSerializer):
    # نکته حیاتی: فیلد id را تعریف می‌کنیم تا در آپدیت بتوانیم آن را دریافت کنیم
    id = serializers.IntegerField(required=False)
    
    # فیلدها برای نمایش نام (Read Only)
    province_name = serializers.CharField(source='province.name', read_only=True)
    city_name = serializers.CharField(source='city.name', read_only=True)

    class Meta:
        model = Address
        fields = ['id', 'province', 'province_name', 'city', 'city_name', 'postal_code', 'address']
        extra_kwargs = {
            'province': {'required': True},
            'city': {'required': True},
        }
# ===== سریالایزر ترکیبی ===== #
class CustomerManagementSerializer(serializers.ModelSerializer):
    # ... فیلدهای پروفایل ...
    first_name = serializers.CharField(source='customer_profile.first_name', required=False)
    last_name = serializers.CharField(source='customer_profile.last_name', required=False)
    phone_number = serializers.CharField(source='customer_profile.phone_number', required=False)
    company = serializers.CharField(source='customer_profile.company', required=False, allow_null=True)
    bio = serializers.CharField(source='customer_profile.bio', required=False, allow_null=True)

    # ===== تغییر اصلی: لیست آدرس‌ها ===== #
    # این فیلد هم برای نمایش است و هم برای دریافت اطلاعات (Write)
    addresses = AddressSerializer(many=True, required=False)

    wallet_balance = serializers.DecimalField(
        source='wallet.decimal', max_digits=12, decimal_places=2, read_only=True
    )

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'password', 'is_active', 'is_staff', 
            'first_name', 'last_name', 'phone_number', 'company', 'bio', 
            'addresses', # تغییر نام فیلد به addresses (جمع)
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
