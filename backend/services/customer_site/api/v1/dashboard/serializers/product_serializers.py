from rest_framework import serializers
from core.models import (
    Product, ProductImage, Attachment, GuideType,
    FieldType, ConditionOperator, ConditionAction, MultiSelectOperator
)


# ===== Guide Fields Mixin ===== #
class GuideSerializerMixin(serializers.Serializer):
    guide_text = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    guide_type = serializers.ChoiceField(choices=GuideType.choices, required=False, default=GuideType.INFO)


# ===== Product Image Serializers ===== #
class ProductImageOrderSerializer(serializers.Serializer):
    image_id = serializers.IntegerField()
    order = serializers.IntegerField()


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'product', 'user', 'image', 'order', 'created_at']
        read_only_fields = ['id', 'order', 'created_at']


# ===== Attachment Serializer ===== #
class AttachmentLibrarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Attachment
        fields = ['id', 'product', 'name', 'file', 'created_at']
        read_only_fields = ['id', 'created_at']


# ===== Product List Serializer ===== #
class ProductSerializer(serializers.ModelSerializer):
    detail_url = serializers.HyperlinkedIdentityField(
        view_name='api:v1:dashboard:products-detail',
        lookup_field='id'
    )
    category = serializers.SerializerMethodField()
    images = ProductImageSerializer(source='product_image', many=True, read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'category', 'description',
            'code', 'is_active', 'price', 'show_price', 'has_price', 'has_quantity',
            'price_per_unit', 'detail_url', 'images', 'created_at'
        ]
        read_only_fields = ['id', 'code', 'slug', 'detail_url']

    def get_category(self, obj):
        cat = obj.categories.first()
        return cat.name if cat else "Uncategorized"


# ===== Field Builder Serializers ===== #
class ProductFieldChoiceSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=False, allow_null=True)
    temp_id = serializers.CharField(required=False, allow_null=True,
        help_text="ID موقت برای فیلدهای جدید (از فرانت‌اند)")
    title = serializers.CharField()
    numeric_value = serializers.DecimalField(max_digits=14, decimal_places=2, default=0.0)
    order = serializers.IntegerField(default=0)
    is_default = serializers.BooleanField(default=False)


class ProductFieldConditionSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=False, allow_null=True)
    trigger_field_id = serializers.CharField(  # CharField چون ممکنه temp_id باشه
        help_text="ID یا temp_id فیلد trigger"
    )
    operator = serializers.ChoiceField(choices=ConditionOperator.choices)
    trigger_choice_id = serializers.CharField(required=False, allow_null=True,
        help_text="ID یا temp_id گزینه trigger")
    trigger_value_text = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    action = serializers.ChoiceField(choices=ConditionAction.choices)

class ProductFieldSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=False, allow_null=True)
    temp_id = serializers.CharField(required=False, allow_null=True,
        help_text="ID موقت برای فیلدهای جدید")
    title = serializers.CharField()
    description = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    field_type = serializers.ChoiceField(choices=FieldType.choices)
    multi_select_operator = serializers.ChoiceField(
        choices=MultiSelectOperator.choices, 
        default='add'
    )
    numeric_value = serializers.DecimalField(max_digits=14, decimal_places=2, default=0.0)
    is_required = serializers.BooleanField(default=False)
    is_active = serializers.BooleanField(default=True)
    is_quantity_field = serializers.BooleanField(default=False)
    order = serializers.IntegerField(default=0)
    choices = ProductFieldChoiceSerializer(many=True, required=False, allow_empty=True)
    conditions = ProductFieldConditionSerializer(many=True, required=False, allow_empty=True)


class ProductFieldsBulkSyncSerializer(serializers.Serializer):
    fields = serializers.ListField(child=ProductFieldSerializer(), allow_empty=True)


# ===== Formula Builder Serializers ===== #
class ProductFormulaSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=False, allow_null=True)
    title = serializers.CharField()
    condition_expression = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    calculation_expression = serializers.CharField()


class ProductFormulasBulkSyncSerializer(serializers.Serializer):
    formulas = serializers.ListField(child=ProductFormulaSerializer(), allow_empty=True)


# ===== Product Shell Serializer ===== #
class ProductShellSerializer(GuideSerializerMixin, serializers.ModelSerializer):
    category_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    subcategory_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    category_info = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'category_id', 'subcategory_id', 'category_info',
            'description', 'code', 'is_active', 'has_price', 'has_quantity',
            'price', 'show_price', 'price_per_unit', 'guide_text', 'guide_type'
        ]
        read_only_fields = ['id', 'code', 'slug']

    def validate(self, attrs):
        category_id = attrs.get('category_id')
        subcategory_id = attrs.get('subcategory_id')

        if category_id and subcategory_id and category_id == subcategory_id:
            raise serializers.ValidationError({
                "subcategory_id": "دسته‌بندی اصلی و زیردسته نمی‌توانند یکسان باشند."
            })
            
        return attrs

    def get_category_info(self, obj):
        categories = list(obj.categories.select_related('parent').all())
        if not categories:
            return None


        selected_cat = categories[0]

        for cat in categories:
            if cat.parent_id is not None:
                selected_cat = cat
                break

        return {
            "id": selected_cat.id, 
            "name": selected_cat.name,
            "parent_id": selected_cat.parent.id if selected_cat.parent else None,
            "parent_name": selected_cat.parent.name if selected_cat.parent else None,
        }

# ===== Core Create/Update Serializer ===== #
class ProductCoreCreateSerializer(serializers.Serializer):
    shell = ProductShellSerializer(required=True)


# ===== Read-Only Field/Choice/Condition Serializers (برای خروجی Detail) ===== #
class ProductFieldChoiceReadSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    title = serializers.CharField()
    numeric_value = serializers.DecimalField(max_digits=14, decimal_places=2)
    order = serializers.IntegerField()
    is_default = serializers.BooleanField()


class ProductFieldConditionReadSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    trigger_field_id = serializers.IntegerField()
    operator = serializers.CharField()
    trigger_choice_id = serializers.IntegerField(allow_null=True)
    trigger_value_text = serializers.CharField(allow_null=True)
    action = serializers.CharField()


class ProductFieldReadSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    title = serializers.CharField()
    description = serializers.CharField(allow_null=True)
    field_type = serializers.CharField()
    numeric_value = serializers.DecimalField(max_digits=14, decimal_places=2)
    is_required = serializers.BooleanField()
    is_active = serializers.BooleanField()
    is_quantity_field = serializers.BooleanField()
    order = serializers.IntegerField()
    multi_select_operator = serializers.CharField()
    choices = ProductFieldChoiceReadSerializer(many=True)
    conditions = ProductFieldConditionReadSerializer(source='applied_conditions', many=True)


class ProductFormulaReadSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    title = serializers.CharField()
    condition_expression = serializers.CharField(allow_null=True)
    calculation_expression = serializers.CharField()
    currency = serializers.CharField()


# ===== Product Detail Serializer ===== #
class ProductDetailSerializer(serializers.Serializer):
    shell = ProductShellSerializer(source='*')
    fields = ProductFieldReadSerializer(many=True, read_only=True)
    formulas = ProductFormulaReadSerializer(many=True, read_only=True)
    images = ProductImageSerializer(source='product_image', many=True, read_only=True)
    attachments = AttachmentLibrarySerializer(source='product_attachment', many=True, read_only=True)


# ===== Media Sync Serializer ===== #
class ProductMediaSyncSerializer(serializers.Serializer):
    attachment_ids_to_link = serializers.ListField(child=serializers.IntegerField(), required=False)
    attachment_ids_to_unlink = serializers.ListField(child=serializers.IntegerField(), required=False)
    image_orders = serializers.ListField(child=ProductImageOrderSerializer(), required=False, allow_null=True)