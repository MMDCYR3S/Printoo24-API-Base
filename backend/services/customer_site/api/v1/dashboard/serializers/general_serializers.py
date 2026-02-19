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

# ===== Province List ===== #
class ProvinceSerialzier(serializers.ModelSerializer):
    """
    سریالایزر برای استان
    """
    class Meta:
        model = Province
        fields = ["id", "name"]

# ===== City List ===== #
class CitySerialzier(serializers.ModelSerializer):
    """
    سریالایزر برای استان
    """
    class Meta:
        model = City
        fields = ["id", "name", "province"]


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
        images = getattr(obj, 'product_image', None)
        if images and images.exists():
            main_image = images.order_by('order', 'id').first()
            if main_image and main_image.image:
                request = self.context.get('request')
                if request:
                    return request.build_absolute_uri(main_image.image.url)
                return main_image.image.url
        
        # ===== اگر عکس نبود ===== #
        request = self.context.get('request')
        no_image_path = '/static/images/no-image.png'
        if request:
            return request.build_absolute_uri(no_image_path)
        return no_image_path

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
        fields = ['id', 'name', 'banner_box', 'detail_url', 'products']

# ========== PARENT CATEGORY LIST SERIALIZER ========== #
class ParentCategoryListSerializer(serializers.ModelSerializer):
    """
    مخصوص لیست والدها: بهینه شده برای جلوگیری از کرش کردن سرور
    """
    detail_url = serializers.HyperlinkedIdentityField(
        view_name='api:v1:dashboard:product_category_dashboard-detail',
        lookup_field='id'
    )
    banner_wide_url = serializers.CharField(source='get_banner_wide_url', read_only=True)
    children = CategoryLinkSerializer(many=True, read_only=True, source='get_children')
    children_count = serializers.IntegerField(read_only=True) # مقدار را از annotate می گیریم
    products_preview = serializers.SerializerMethodField()

    class Meta:
        model = ProductCategory
        fields = [
            'id', 'name', 'slug', 'detail_url', 'is_active',
            'banner_wide', 'banner_box', 'banner_wide_url', 'children',
            'children_count', 'products_preview', 'created_at'
        ]
        
    def get_products_preview(self, obj):
        """نمایش فقط ۵ محصول اول برای جلوگیری از سنگین شدن ریسپانس"""
        products = obj.products.all()[:5]
        return ProductMinimalSerializer(products, many=True, context=self.context).data
    
# ===== سریالایزر اطلاعات والد (Nested Serializer) ===== #
class ParentInfoSerializer(serializers.Serializer):
    """
    نمایش اطلاعات خلاصه شده والد دسته‌بندی.
    این سریالایزر برای جلوگیری از تودرتو شدن بی‌مورد و ساده کردن خروجی استفاده می‌شود.
    """
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(read_only=True)
    slug = serializers.SlugField(read_only=True)

# ===== سریالایزر کمکی برای تصاویر ===== #
class CategoryBannerSerializer(serializers.Serializer):
    wide = serializers.CharField(read_only=True, allow_null=True)
    box = serializers.CharField(read_only=True, allow_null=True)

# ===== سریالایزر لیست زیردسته‌ها (اصلاح شده) ===== #
class SubcategoryWithParentSerializer(serializers.Serializer):
    """
    نمایش لیست مسطح زیردسته‌ها به همراه اطلاعات والد و تصاویر.
    """
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(read_only=True)
    slug = serializers.SlugField(read_only=True)
    description = serializers.CharField(read_only=True, allow_null=True) # توضیحات هم بود که اضافه کردم
    is_active = serializers.BooleanField(read_only=True)
    
    # ===== اضافه کردن فیلد تصاویر ===== #
    banners = CategoryBannerSerializer(read_only=True)
    
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
class CategoryBulkUpsertSerializer(serializers.ModelSerializer):
    """
    سریالایزر هوشمند برای ایجاد و ویرایش گروهی.
    - فیلد id: اختیاری (اگر باشد یعنی آپدیت، نباشد یعنی ایجاد)
    - فیلد parent_slug: برای اتصال به والد
    - سایر فیلدها: مستقیماً از مدل ارث‌بری می‌شوند.
    """
    id = serializers.IntegerField(required=False, allow_null=True)
    
    parent_slug = serializers.SlugField(
        max_length=150, 
        required=False, 
        allow_null=True, 
        allow_blank=True, 
        write_only=True
    )

    class Meta:
        model = ProductCategory
        fields = [
            'id', 'name', 'slug', 'description', 
            'banner_wide', 'banner_box', 
            'is_active', 'parent_slug'
        ]
        extra_kwargs = {
            'slug': {'required': False},
            'name': {'required': True},
        }

    def validate(self, attrs):
        """
        اگر چک خاصی نیاز داری اینجا اضافه کن.
        مثلا: نمیشه والد خودت باشی (در سرویس هندل میشه البته)
        """
        return attrs

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

# ===== ADDRESS SERIALIZERS ===== #
class AddressReadSerializer(serializers.ModelSerializer):
    """ نمایش آدرس """
    province_name = serializers.CharField(source='province.name', read_only=True)
    city_name = serializers.CharField(source='city.name', read_only=True)

    class Meta:
        model = Address
        fields = ['id', 'province', 'province_name', 'city', 'city_name', 'postal_code', 'address']

class AddressWriteSerializer(serializers.Serializer):
    """ دریافت ورودی آدرس """
    id = serializers.IntegerField(required=False) # برای ویرایش
    province = serializers.PrimaryKeyRelatedField(queryset=Province.objects.all())
    city = serializers.PrimaryKeyRelatedField(queryset=City.objects.all())
    
    # اصلاح: اختیاری کردن کد پستی
    postal_code = serializers.CharField(required=False, allow_blank=True, allow_null=True, max_length=10)
    address = serializers.CharField()

    def validate_postal_code(self, value):
        """ تبدیل رشته خالی به None """
        if not value:
            return None
        return value

# ===== CUSTOMER READ SERIALIZER ===== #
class CustomerReadSerializer(serializers.ModelSerializer):
    """
    مخصوص نمایش لیست و جزئیات.
    """
    first_name = serializers.CharField(source='customer_profile.first_name', read_only=True)
    last_name = serializers.CharField(source='customer_profile.last_name', read_only=True)
    phone_number = serializers.CharField(source='customer_profile.phone_number', read_only=True)
    company = serializers.CharField(source='customer_profile.company', read_only=True)
    bio = serializers.CharField(source='customer_profile.bio', read_only=True)
    
    addresses = AddressReadSerializer(many=True, read_only=True)
    
    wallet_balance = serializers.DecimalField(
        source='wallet.balance', max_digits=12, decimal_places=2, read_only=True
    )

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'is_active', 
            'first_name', 'last_name', 'phone_number', 'company', 'bio', 
            'addresses', 'wallet_balance', 'created_at'
        ]

# ===== CUSTOMER WRITE SERIALIZER ===== # 
class CustomerWriteSerializer(serializers.ModelSerializer):
    """
    مخصوص ایجاد و ویرایش.
    """
    first_name = serializers.CharField(required=False, allow_blank=True)
    last_name = serializers.CharField(required=False, allow_blank=True)
    phone_number = serializers.CharField(required=False, allow_blank=True)
    company = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    bio = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    addresses = AddressWriteSerializer(many=True, required=False)

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'password', 'is_active', 
            'first_name', 'last_name', 'phone_number', 'company', 'bio', 
            'addresses'
        ]
        extra_kwargs = {
            'password': {'write_only': True, 'required': False},
            'username': {'required': True},
            'email': {'required': False, 'allow_blank': True},
        }

    def validate_email(self, value):
        """
        جلوگیری از خطای Unique Constraint برای رشته‌های خالی.
        اگر ایمیل خالی بود، آن را None کن تا دیتابیس ارور ندهد.
        """
        if not value:
            return None

        user_id = self.instance.id if self.instance else None
        if User.objects.filter(email=value).exclude(id=user_id).exists():
            raise serializers.ValidationError("این ایمیل قبلا ثبت شده است.")
            
        return value

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
