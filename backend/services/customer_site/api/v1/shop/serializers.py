from rest_framework import serializers
from core.models import (
    Product, ProductCategory,
    ProductImage, ProductComment, Attachment,
    ProductField, ProductFieldChoice, ProductFieldCondition, ProductFormula
)

# ==========================================
# 1. BASE SERIALIZERS
# ==========================================

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductCategory
        fields = ['id', 'name', 'slug']


# ==========================================
# 2. MEDIA SERIALIZERS
# ==========================================

class ProductImageSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = ProductImage
        fields = ['id', 'image_url', 'order']

    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image:
            return request.build_absolute_uri(obj.image.url) if request else obj.image.url
        return None


class AttachmentSerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = Attachment
        fields = ['id', 'name', 'file_url', 'created_at']

    def get_file_url(self, obj):
        request = self.context.get('request')
        if obj.file:
            return request.build_absolute_uri(obj.file.url) if request else obj.file.url
        return None


# ==========================================
# 3. FIELD BUILDER SERIALIZERS (Read-Only)
# ==========================================

class ProductFieldChoiceOutputSerializer(serializers.ModelSerializer):
    title = serializers.CharField(source='choice_dict.title', read_only=True)
    numeric_value = serializers.DecimalField(
        source='choice_dict.numeric_value', 
        max_digits=14, 
        decimal_places=2, 
        read_only=True
    )

    class Meta:
        model = ProductFieldChoice
        fields = ['id', 'title', 'numeric_value', 'order']


class ProductFieldConditionOutputSerializer(serializers.ModelSerializer):
    trigger_field_id = serializers.IntegerField(source='trigger_field.id')
    trigger_choice_id = serializers.IntegerField(
        source='trigger_choice.id', allow_null=True
    )

    class Meta:
        model = ProductFieldCondition
        fields = ['id', 'trigger_field_id', 'operator', 'trigger_choice_id', 'trigger_value_text', 'action']


class ProductFieldOutputSerializer(serializers.ModelSerializer):
    title = serializers.CharField(source='field_dict.title', read_only=True)
    description = serializers.CharField(source='field_dict.description', read_only=True, allow_null=True)
    field_type = serializers.CharField(source='field_dict.field_type', read_only=True)
    
    is_quantity_field = serializers.BooleanField(source='field_dict.is_quantity_field', read_only=True)

    choices = ProductFieldChoiceOutputSerializer(many=True, read_only=True)
    conditions = ProductFieldConditionOutputSerializer(
        source='applied_conditions', many=True, read_only=True
    )

    class Meta:
        model = ProductField
        fields = [
            'id', 'title', 'description', 'field_type',
            'numeric_value', 'is_required', 'is_active',
            'is_quantity_field', 'order', 'choices', 'conditions'
        ]


# ==========================================
# 4. FORMULA SERIALIZER (Read-Only)
# ==========================================

class ProductFormulaOutputSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductFormula
        fields = ['id', 'title', 'condition_expression', 'calculation_expression', 'currency']


# ==========================================
# 5. PRODUCT LIST SERIALIZER
# ==========================================

class ProductListSerializer(serializers.ModelSerializer):
    category = serializers.SerializerMethodField()
    thumbnail = serializers.SerializerMethodField()
    detail_url = serializers.HyperlinkedIdentityField(
        view_name='api:v1:shop:detail',
        lookup_field='slug'
    )

    class Meta:
        model = Product
        fields = ['id', 'name', 'slug', 'price', 'show_price', 'has_price', 'category', 'thumbnail', 'detail_url']

    def get_category(self, obj):
        assigned_cats = obj.categories.select_related("parent").all()

        subcategory = next((c for c in assigned_cats if c.parent is not None), None)
        
        if subcategory:
            return {
                "parent_category": subcategory.parent.name,
                "children_category": subcategory.name
            }

        root_cat = next((c for c in assigned_cats if c.parent is None), None)
        return {
            "parent_category": root_cat.name if root_cat else None,
            "children_category": None
        }

    def get_thumbnail(self, obj):
        img = obj.product_image.first()
        if img:
            request = self.context.get('request')
            return request.build_absolute_uri(img.image.url) if request else img.image.url
        return None


# ==========================================
# 6. PRODUCT DETAIL SERIALIZER
# ==========================================

class ProductDetailSerializer(serializers.ModelSerializer):
    """
    سریالایزر صفحه جزئیات محصول برای مشتری.
    شامل اطلاعات پایه، فیلدهای داینامیک، فرمول‌ها و رسانه.
    """
    category = serializers.SerializerMethodField()
    images = ProductImageSerializer(source='product_image', many=True, read_only=True)
    attachments = AttachmentSerializer(source='product_attachment', many=True, read_only=True)
    fields = ProductFieldOutputSerializer(many=True, read_only=True)
    formulas = ProductFormulaOutputSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'code', 'description',
            'has_price', 'price', 'show_price', 'price_per_unit',
            'has_quantity', 'is_active',
            'guide_text', 'guide_type',
            'category', 'fields', 'formulas', 'images', 'attachments',
        ]

    def get_category(self, obj):
        assigned_cat = obj.categories.first()
        if not assigned_cat:
            return {"parent_category": None, "children_category": None}

        return {
            "parent_category": assigned_cat.parent.name if assigned_cat.parent else assigned_cat.name,
            "children_category": assigned_cat.name,
            "slug": assigned_cat.slug,
        }


# ==========================================
# 7. FEEDBACK SERIALIZERS
# ==========================================

class SubmitReviewSerializer(serializers.Serializer):
    score = serializers.IntegerField(required=False, min_value=1, max_value=5)
    message = serializers.CharField(required=False, allow_blank=False)

    def validate(self, data):
        if 'score' not in data and 'message' not in data:
            raise serializers.ValidationError("لطفاً حداقل یک امتیاز یا متن نظر وارد کنید.")
        return data


class ReplySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductComment
        fields = ['id', 'name', 'message', 'created_at']


class CommentListSerializer(serializers.ModelSerializer):
    replies = ReplySerializer(many=True, read_only=True)

    class Meta:
        model = ProductComment
        fields = ['id', 'name', 'message', 'created_at', 'replies']


class ProductFeedbackStatsSerializer(serializers.Serializer):
    average_rating = serializers.FloatField()
    total_ratings = serializers.IntegerField()
    comments = CommentListSerializer(many=True)


# ==========================================
# 8. CATEGORY & LANDING SERIALIZERS
# ==========================================

class ProductSummarySerializer(serializers.ModelSerializer):
    category = serializers.SerializerMethodField()
    thumbnail = serializers.SerializerMethodField()
    # price = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['id', 'name', 'slug', 'show_price', 'thumbnail', 'category']

    def get_thumbnail(self, obj):
        first_image = obj.product_image.first()
        if first_image and first_image.image:
            request = self.context.get('request')
            return request.build_absolute_uri(first_image.image.url) if request else first_image.image.url
        return None
    
    # def get_price(self, obj):
    #     if obj.show_price:
    #         return f"{obj.show_price}"
    #     return None
    
    def get_category(self, obj):
        assigned_cats = obj.categories.select_related("parent").all()
        subcategory = next((c for c in assigned_cats if c.parent is not None), None)
        if subcategory:
            return {
                "parent_category": subcategory.parent.name,
                "children_category": subcategory.name
            }
        root_cat = next((c for c in assigned_cats if c.parent is None), None)
        return {
            "parent_category": root_cat.name if root_cat else None,
            "children_category": None
        }


class SubCategoryTinySerializer(serializers.Serializer):
    name = serializers.CharField()
    slug = serializers.CharField()
    thumbnail = serializers.URLField(allow_null=True, required=False)
    link = serializers.CharField(allow_null=True, required=False)


class CategoryInfoSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    slug = serializers.CharField()
    description = serializers.CharField(allow_null=True)
    order = serializers.CharField()
    banners = serializers.DictField()
    breadcrumbs = serializers.ListField(child=serializers.DictField(), required=False)


class CategoryLandingPageSerializer(serializers.Serializer):
    category_info = CategoryInfoSerializer()
    sub_categories = SubCategoryTinySerializer(many=True)
    products = ProductSummarySerializer(many=True)

# ========== Live Price Calculation ========== #
class LivePriceCalculationSerializer(serializers.Serializer):
    """
    سریالایزر برای دریافت داینامیک انتخاب‌های کاربر از فرانت‌اند.
    نمونه ورودی:
    {
        "selections": {
            "12": "45",       # فیلد آیدی 12 -> گزینه 45
            "15": "1000",     # فیلد آیدی 15 -> عدد 1000
            "20": ["1", "2"]  # فیلد چند انتخابی
        }
    }
    """
    selections = serializers.DictField(
        child=serializers.JSONField(), 
        required=True,
        help_text="دیکشنری شامل آیدی فیلدها به عنوان کلید و مقادیر انتخابی کاربر"
    )
