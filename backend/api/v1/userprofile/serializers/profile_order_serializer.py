from rest_framework import serializers
from core.models import Order, OrderItem, OrderItemFile, Product, Address, Quotation, Invoice

# ===== Quotation ===== #
class QuotationSerializer(serializers.ModelSerializer):
    product_image_url = serializers.SerializerMethodField()
    
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

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'name', 'quantity', 'price', 'specs', 'design_files']

    def get_specs(self, obj):
        """
        استخراج و فرمت‌دهی اطلاعات فنی از JSON Field (item.items)
        منطبق با معماری جدید: دریافت لیستی از ویژگی‌های داینامیک انتخاب شده
        """
        raw_data = obj.items if isinstance(obj.items, list) else []
        
        detailed_options = []
        for opt in raw_data:
            detailed_options.append({
                "option_group": opt.get('field_title', 'نامشخص'),
                "selections": [{
                    "label": str(opt.get('value', '---')),
                    "is_tiered": False,
                }]
            })

        return {
            "quantity_label": str(obj.quantity),
            "has_design": obj.files.exists(),
            "options_detail": detailed_options
        }

    def _format_val(self, val_data):
        """ فرمت‌دهی به هر مقدار انتخاب شده همراه با ذکر وابستگی """
        base_text = val_data.get('label', 'N/A')
        deps = val_data.get('dependencies', [])
        if deps:
            dep_text = " + ".join([f"{d['required_value_name']}" for d in deps])
            return f"{base_text} (وابسته به {dep_text})"
        return base_text


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
    status_code = serializers.CharField(source='current_status.internal_code', read_only=True)
    type_display = serializers.CharField(source='get_type_display', read_only=True)
    full_address = serializers.CharField(source='address', read_only=True)
    
    # ===== نمایش آدرس‌ کاربر ===== #
    address_id = serializers.PrimaryKeyRelatedField(
        queryset=Address.objects.all(),
        source="address",
        write_only=True,
        required=True
    )
    address = serializers.SerializerMethodField(read_only=True)

    # ===== فیلدهای مالی ===== #
    paid_amount = serializers.SerializerMethodField(read_only=True)
    remaining_amount = serializers.SerializerMethodField(read_only=True)

    def get_paid_amount(self, obj):
        if hasattr(obj, 'invoice') and obj.invoice:
            return str(obj.invoice.paid_amount)
        return "0"

    def get_remaining_amount(self, obj):
        if hasattr(obj, 'invoice') and obj.invoice:
            return str(obj.invoice.remaining_amount)
        return str(obj.total_price)

    def get_address(self, obj):
        if obj.address:
            return f"{obj.address.province} - {obj.address.city} - {obj.address.address}" 
        return obj.full_address

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            self.fields['address_id'].queryset = Address.objects.filter(user=request.user)

    class Meta:
        model = Order
        fields = [
            'id', 'user', "recipient_name", "recipient_phone",
            'status', 'status_code', 'type_display', 'total_price',
            'paid_amount', 'remaining_amount',
            'order_code', 'created_at', "address_id", "address", "full_address"
        ]


# ===== Order Detail Serializer ===== #
class InvoiceOrderSummarySerializer(serializers.ModelSerializer):
    """ سریالایزر سفارش که فقط تک آیتم مربوطه را برمی‌گرداند """
    status_display = serializers.CharField(source='current_status.name', read_only=True)
    full_address = serializers.SerializerMethodField(read_only=True)
    single_item = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'order_code', 'status_display', 'total_price', 
            'full_address', 'recipient_name', 'recipient_phone',
            'created_at', 'single_item'
        ]

    def get_full_address(self, obj):
        if obj.address:
            return f"{obj.address.province} - {obj.address.city} - {obj.address.address}" 
        return obj.full_address

    def get_single_item(self, obj):
        item = obj.order_item_order.first()
        if item:
            return OrderItemDetailSerializer(item, context=self.context).data
        return None

# ===== Full Invoice Detail Serializer ===== #
class FullInvoiceDetailSerializer(serializers.ModelSerializer):
    """ سریالایزر جامع فاکتور به همراه جزئیات کامل سفارش و آیتم """
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    order_details = InvoiceOrderSummarySerializer(source='order', read_only=True)
    
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
            'order_details'
        ]