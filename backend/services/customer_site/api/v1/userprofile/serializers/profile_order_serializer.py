from rest_framework import serializers
from core.models import Order, OrderItem, OrderItemFile, Product, Address, Quotation, Invoice

# ===== Quotation ===== #
class QuotationSerializer(serializers.ModelSerializer):
    product_image_url = serializers.SerializerMethodField()
    # snapshot_details = serializers.SerializerMethodField()
    
    class Meta:
        model = Quotation
        fields = [
            'id',
            'quotation_number',
            'customer_name',
            'product_name',
            'product_image_url',
            'product_snapshot',
            'quantity',
            'total_price',
            'created_at',
            'status',
        ]

    def get_product_image_url(self, obj):
        request = self.context.get('request')
        if obj.product_image:
            return request.build_absolute_uri(obj.product_image.url) if request else obj.product_image.url
        return None

    # def get_snapshot_details(self, obj):
    #     """
    #     تبدیل JSON ذخیره شده به فرمت قابل نمایش
    #     """
    #     raw_data = obj.product_snapshot or {}
    #     details = raw_data.get('details', {})
        
    #     return {
    #         "dimensions": f"{details.get('width', 0)} x {details.get('height', 0)}",
    #         "material": details.get('material_name', 'نامشخص'),
    #         "features": [
    #             f"{opt['name']}: {opt['value']}" for opt in details.get('options', [])
    #         ]
    #     }

# ===== Product Summary ===== #
class ProductSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['name', 'slug', 'code']

class ProductMinimalSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['name', 'code', 'slug', 'image']

    def get_image(self, obj):
        """واکشی اولین تصویر محصول با اولویت ترتیب نمایش"""
        request = self.context.get('request')
        first_image = obj.product_image.all().order_by('order').first()
        if first_image and first_image.image:
            return request.build_absolute_uri(first_image.image.url) if request else first_image.image.url
        return None

# ===== Order Item File Serializer =====
class OrderItemFileSerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()
    requirement_name = serializers.CharField(source='requirement.spec.name', read_only=True)

    class Meta:
        model = OrderItemFile
        fields = ['id', 'requirement_name', 'file_url']

    def get_file_url(self, obj):
        request = self.context.get('request')
        if obj.file:
            return request.build_absolute_uri(obj.file.url) if request else obj.file.url
        return None

# ===== Order Item Detail (The Core) =====
class OrderItemDetailSerializer(serializers.ModelSerializer):
    product = ProductMinimalSerializer(read_only=True)
    design_files = OrderItemFileSerializer(source='files', many=True, read_only=True)
    specs = serializers.SerializerMethodField()
    pricing_breakdown = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'name', 'quantity', 'price', 'specs', 'design_files', 'pricing_breakdown']

    def get_specs(self, obj):
        """
        استخراج هوشمند مشخصات فنی از JSON ذخیره شده در OrderItem.
        """
        raw_data = obj.items or {}
        meta = raw_data.get('meta', {})
        
        # ۱. استخراج اطلاعات سایز و ابعاد
        size_info = meta.get('size_info', {})
        dimensions = f"{size_info.get('width')}x{size_info.get('height')} cm" if size_info.get('width') else "استاندارد"
        size_name = size_info.get('size_name', 'استاندارد')

        # ۲. استخراج اطلاعات تیراژ
        qty_info = meta.get('quantity_info', {})
        quantity_label = qty_info.get('quantity_text', str(obj.quantity))

        # ۳. پردازش غنی آپشن‌ها و وابستگی‌ها
        raw_options = raw_data.get('options', [])
        processed_options = []

        for opt in raw_options:
            opt_label = opt.get('option_label', 'N/A')
            type_ptr = opt.get('type')
            
            selected_texts = []
            
            if type_ptr == 'selection':
                val = opt.get('value', {})
                selected_texts.append(self._format_val(val))
            elif type_ptr == 'multi_selection':
                for val in opt.get('values', []):
                    selected_texts.append(self._format_val(val))
            elif type_ptr == 'raw':
                selected_texts.append(f"{opt.get('value')} (ورودی کاربر)")

            processed_options.append({
                "name": opt_label,
                "values": selected_texts
            })

        return {
            "size_name": size_name,
            "dimensions": dimensions,
            "quantity_label": quantity_label,
            "has_design": meta.get('has_design', False),
            "options": processed_options
        }

    def _format_val(self, val_data):
        """ فرمت‌دهی به هر مقدار انتخاب شده همراه با ذکر وابستگی """
        base_text = val_data.get('label', 'N/A')
        deps = val_data.get('dependencies', [])
        if deps:
            dep_text = " + ".join([f"{d['required_value_name']}" for d in deps])
            return f"{base_text} (وابسته به {dep_text})"
        return base_text

    def get_pricing_breakdown(self, obj):
        """ نمایش ریز محاسبات ماشین‌حساب به مشتری """
        raw_data = obj.items or {}
        return raw_data.get('meta', {}).get('price_breakdown', {})

# ===== Order With Details Serializer ===== #
class OrderWithDetailsSerializer(serializers.ModelSerializer):
    order_item = OrderItemDetailSerializer(source="order_item_order", many=True, read_only=True)
    status_display = serializers.CharField(source='current_status.name', read_only=True)
    
    class Meta:
        model = Order
        fields = [
            'id', 'order_code', 'status_display', 'total_price', 
            'full_address', 'recipient_name', 'recipient_phone',
            'created_at', 'order_item'
        ]

# ===== Order Detail (Main) ===== #
class OrderSerializer(serializers.ModelSerializer):
    status = serializers.CharField(source='current_status.name', read_only=True)
    type_display = serializers.CharField(source='get_type_display', read_only=True)
    
    # آدرس (هم دریافت ID برای ثبت، هم نمایش متن برای خواندن)
    address_id = serializers.PrimaryKeyRelatedField(
        queryset=Address.objects.all(),
        source="address",
        write_only=True,
        required=True
    )
    address = serializers.StringRelatedField(read_only=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            self.fields['address_id'].queryset = Address.objects.filter(user=request.user)

    class Meta:
        model = Order
        fields = [
            'id', 'user', "recipient_name", "recipient_phone",
            'status', 'type_display', 'total_price',
            'order_code', 'created_at', "address_id", "address"
        ]

# ===== User Invoice Serializer ===== #
class UserInvoiceSerializer(serializers.ModelSerializer):
    """
    سریالایزر نمایش فاکتور نهایی به مشتری
    """
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Invoice
        fields = [
            'id',
            'invoice_number',
            'items_amount',
            'services_amount',
            'tax_amount',
            'discount_amount',
            'final_amount',
            'paid_amount',
            'remaining_amount',
            'description',
            'status',
            'status_display',
            'issued_at',
            'finalized_at',
        ]
