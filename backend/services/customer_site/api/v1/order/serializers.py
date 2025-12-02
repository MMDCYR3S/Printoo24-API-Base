from rest_framework import serializers
from core.models import Order, OrderItem, OrderItemFile, Product, Address

# ===== Product Summary Serializer ===== #
class ProductSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['name', 'slug']

# ===== Order Item File Serializer ===== #
class OrderItemFileSerializer(serializers.ModelSerializer):
    """
    Serializer for displaying final order files.
    """
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

# ===== Order Item Detail Serializer ===== #
class OrderItemDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for order item details, extracting specs from JSON.
    """
    product_name = serializers.CharField(source='product.name', read_only=True)
    design_files = OrderItemFileSerializer(source='files', many=True, read_only=True)
    
    # Details field extracted from JSON
    specs = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = [
            'id', 
            'product_name', 
            'quantity', 
            'price', 
            'specs', 
            'design_files'
        ]

    def get_specs(self, obj):
        """
        Parses the JSON `items_data` into a clean format for the frontend.
        """
        raw_data = obj.items_data or {}
        details = raw_data.get('details', {})
        
        # Fallback for old data or if structure is flat
        if not details and 'material_name' not in raw_data:
             return raw_data 

        # Construct clean output
        return {
            "dimensions": f"{details.get('width')} x {details.get('height')} cm",
            "material": details.get('material_name') or details.get('material', {}).get('name'),
            "size": details.get('size_name'),
            "has_design": details.get('has_design'),
            "options": [
                f"{opt['name']}: {opt['value']}" 
                for opt in details.get('options', [])
            ]
        }

# ===== Order Serializer (Main) ===== #
class OrderSerializer(serializers.ModelSerializer):
    """
    Main serializer for creating and viewing orders.
    """
    user = serializers.StringRelatedField(read_only=True)
    status = serializers.CharField(source='order_status.name', read_only=True)
    type_display = serializers.CharField(source='get_type_display', read_only=True)
    
    # Display full address string in read operations
    address = serializers.SerializerMethodField()

    # Input field for Address ID (Write Only) - REQUIRED
    address_id = serializers.PrimaryKeyRelatedField(
        queryset=Address.objects.all(),
        source="address",
        write_only=True,
        required=True,  # Explicitly required
        allow_null=False
    )
    
    # Items (Read Only)
    items = OrderItemDetailSerializer(many=True, read_only=True)
    
    total_price = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter address queryset to current user's addresses
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            self.fields['address_id'].queryset = Address.objects.filter(user=request.user)

    class Meta:
        model = Order
        fields = [
            'id', 
            'user', 
            'status', 
            'type_display', 
            'total_price', 
            'address', 
            'address_id', # Included for input
            'created_at', 
            'items'
        ]

    def get_address(self, obj):
        if obj.address:
            return str(obj.address)
        return "Address not found"
