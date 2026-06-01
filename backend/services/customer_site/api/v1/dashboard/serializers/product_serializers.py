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
    temp_id = serializers.CharField(
        required=False, 
        allow_null=True,
        error_messages={
            'blank': 'شناسه موقت گزینه نمی‌تواند خالی باشد.'
        }
    )
    title = serializers.CharField(
        error_messages={
            'blank': 'عنوان گزینه نمی‌تواند خالی باشد.',
            'required': 'ارسال عنوان گزینه الزامی است.'
        }
    )
    numeric_value = serializers.DecimalField(
        max_digits=14, 
        decimal_places=2, 
        default=0.0,
        error_messages={
            'invalid': 'مقدار عددی گزینه معتبر نیست.',
            'required': 'ارسال مقدار عددی گزینه الزامی است.'
        }
    )
    order = serializers.IntegerField(
        default=0,
        error_messages={'invalid': 'ترتیب نمایش باید یک عدد صحیح باشد.'}
    )
    is_default = serializers.BooleanField(
        default=False,
        error_messages={'invalid': 'مقدار گزینه پیش‌فرض باید Boolean باشد.'}
    )

    def validate(self, attrs):
        if not attrs.get('id') and not attrs.get('temp_id'):
            raise serializers.ValidationError({"temp_id": "برای گزینه‌ها، ارسال id یا temp_id الزامی است."})
        return attrs


class ProductFieldConditionSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=False, allow_null=True)
    trigger_field_id = serializers.CharField(
        error_messages={
            'blank': 'شناسه فیلد شرط نمی‌تواند خالی باشد.',
            'required': 'ارسال شناسه فیلد شرط الزامی است.'
        }
    )
    operator = serializers.ChoiceField(
        choices=ConditionOperator.choices,
        error_messages={
            'invalid_choice': 'عملگر انتخابی معتبر نیست.',
            'required': 'انتخاب عملگر شرط الزامی است.'
        }
    )
    trigger_choice_id = serializers.CharField(
        required=False, 
        allow_null=True,
        error_messages={'blank': 'شناسه گزینه شرط نمی‌تواند خالی باشد.'}
    )
    trigger_value_text = serializers.CharField(
        required=False, 
        allow_blank=True, 
        allow_null=True,
        error_messages={'blank': 'متن شرط نمی‌تواند خالی باشد.'}
    )
    action = serializers.ChoiceField(
        choices=ConditionAction.choices,
        error_messages={
            'invalid_choice': 'عملیات انتخابی معتبر نیست.',
            'required': 'انتخاب عملیات شرط الزامی است.'
        }
    )

class ProductFieldSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=False, allow_null=True)
    temp_id = serializers.CharField(
        required=False, 
        allow_null=True,
        error_messages={'blank': 'شناسه موقت فیلد نمی‌تواند خالی باشد.'}
    )
    title = serializers.CharField(
        error_messages={
            'blank': 'عنوان فیلد نمی‌تواند خالی باشد.',
            'required': 'ارسال عنوان فیلد الزامی است.'
        }
    )
    description = serializers.CharField(
        required=False, 
        allow_blank=True, 
        allow_null=True
    )
    field_type = serializers.ChoiceField(
        choices=FieldType.choices,
        error_messages={
            'invalid_choice': 'نوع فیلد انتخابی معتبر نیست.',
            'required': 'انتخاب نوع فیلد الزامی است.'
        }
    )
    multi_select_operator = serializers.ChoiceField(
        choices=MultiSelectOperator.choices, 
        default='add',
        error_messages={'invalid_choice': 'عملگر چندانتخابی معتبر نیست.'}
    )
    numeric_value = serializers.DecimalField(
        max_digits=14, 
        decimal_places=2, 
        default=0.0,
        error_messages={'invalid': 'مقدار عددی فیلد نامعتبر است.'}
    )
    is_required = serializers.BooleanField(default=False)
    is_active = serializers.BooleanField(default=True)
    is_quantity_field = serializers.BooleanField(default=False)
    order = serializers.IntegerField(default=0)
    
    choices = ProductFieldChoiceSerializer(many=True, required=False, allow_empty=True)
    conditions = ProductFieldConditionSerializer(many=True, required=False, allow_empty=True)

    def validate(self, attrs):
        if not attrs.get('id') and not attrs.get('temp_id'):
            raise serializers.ValidationError({"error": "داشتن id یا temp_id برای هر فیلد الزامی است."})
        return attrs


class ProductFieldsBulkSyncSerializer(serializers.Serializer):
    fields = serializers.ListField(
        child=ProductFieldSerializer(), 
        allow_empty=True,
        error_messages={'required': 'لیست فیلدها ارسال نشده است.'}
    )
    def validate(self, attrs):
        fields_data = attrs.get('fields', [])
        condition_errors = []
        
        # ===== درست کردن فیلد ===== #
        valid_field_keys = set()
        valid_choice_keys = set()
        
        for field in fields_data:
            # ===== کلید فیلدهای یکتا ===== #
            f_key = str(field.get('id') or field.get('temp_id'))
            valid_field_keys.add(f_key)
            
            for choice in field.get('choices', []):
                c_key = str(choice.get('id') or choice.get('temp_id'))
                valid_choice_keys.add(c_key)

        # ===== فیلد قسمت مربوط به اعتبارسنجی فیلدها ===== #
        for field in fields_data:
            f_key = str(field.get('id') or field.get('temp_id'))
            
            for cond in field.get('conditions', []):
                trigger_field_id = str(cond.get('trigger_field_id'))
                trigger_choice_id = str(cond.get('trigger_choice_id')) if cond.get('trigger_choice_id') else None

                # ===== وجود فیلدهای پیش‌شرط ===== #
                if trigger_field_id not in valid_field_keys:
                    condition_errors.append({
                        "target_field_id": f_key,
                        "trigger_field_id": trigger_field_id,
                        "error": f"فیلد پیش‌شرط با شناسه '{trigger_field_id}' در لیست فیلدها یافت نشد."
                    })
                
                if trigger_choice_id and trigger_choice_id != 'None':
                    if trigger_choice_id not in valid_choice_keys:
                        condition_errors.append({
                            "target_field_id": f_key,
                            "trigger_choice_id": trigger_choice_id,
                            "error": f"گزینه پیش‌شرط با شناسه '{trigger_choice_id}' یافت نشد."
                        })

        if condition_errors:
            raise serializers.ValidationError({
                "error": condition_errors
            })

        return attrs

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
    title = serializers.CharField(source='choice_dict.title')
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
    # دیتا از جدول FieldDictionary خوانده می‌شود
    title = serializers.CharField(source='field_dict.title')
    description = serializers.CharField(source='field_dict.description', allow_null=True)
    field_type = serializers.CharField(source='field_dict.field_type')
    multi_select_operator = serializers.CharField(source='field_dict.multi_select_operator', allow_null=True, required=False)
    
    is_quantity_field = serializers.BooleanField(source='field_dict.is_quantity_field')
    
    # مقادیر زیر در خود جدول واسط (ProductField) قرار دارند
    numeric_value = serializers.DecimalField(max_digits=14, decimal_places=2, allow_null=True, required=False)
    is_required = serializers.BooleanField()
    is_active = serializers.BooleanField()
    order = serializers.IntegerField()
    
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