from rest_framework import serializers
from core.models import Order, OrderItem, OrderItemFile, Product, Address, Quotation

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
        fields = ['name', 'slug']

# ===== Order Item File ===== #
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

# ===== Order Item Detail ===== #
class OrderItemDetailSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    design_files = OrderItemFileSerializer(source='files', many=True, read_only=True)
    specs = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = [
            'id', 
            'product_name', 
            'quantity', 
            'specs', 
            'design_files'
        ]

    def get_specs(self, obj):
        """
        خواندن اطلاعات از فیلد items (JSONField).
        """
        # ===== خواندن فیلدها از فیلد جیسون ===== #
        raw_data = obj.items or {} 
        
        details = raw_data.get('details', {})
        
        # ===== خواندن اطلاعات از فیلد details ===== #
        if not details and 'material_name' not in raw_data:
             return raw_data 

        return {
            "dimensions": f"{details.get('width')} x {details.get('height')} cm",
            "material": details.get('material_name') or details.get('material', {}).get('name'),
            "size": details.get('size_name'),
            "has_design": details.get('has_design'),
            "options": [
                f"{opt.get('name')}: {opt.get('value')}" 
                for opt in details.get('options', [])
            ]
        }

# ===== Order With Details Serializer ===== #
class OrderWithDetailsSerializer(serializers.ModelSerializer):
    order_item = OrderItemDetailSerializer(source="order_item_order", many=True, read_only=True)
    status_display = serializers.CharField(source='get_current_status_display', read_only=True)
    
    class Meta:
        model = Order
        fields = [
            'id', 'user', 'order_code','current_status', "status_display", 
            'total_price', "full_address",
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
