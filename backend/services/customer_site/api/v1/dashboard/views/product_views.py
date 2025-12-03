from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema

from core.domain.product import ProductDomainService
from ..serializers import (
    ProductShellSerializer, 
    ProductPricingConfigSerializer,
    MaterialSyncSerializer,
    QuantitySyncSerializer,
    OptionAttachWithPriceSerializer,
    OptionPriceUpdateSerializer,
    FileRequirementSyncSerializer
)

# ===== Product Dashboard View Set ===== #
@extend_schema(tags=['Dashboard-Product'])
class ProductDashboardViewSet(viewsets.ModelViewSet):
    """
    مدیریت کامل محصول به صورت مرحله به مرحله (Wizard).
    """
    # سریالایزر پیش‌فرض (برای لیست و Create اولیه)
    serializer_class = ProductShellSerializer
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = ProductDomainService()

    def get_queryset(self):
        return self.service.get_all_active_products()

    # ===== Step 1: Create Shell ===== #
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # ===== انتقال لاجیک ذخیره‌سازی به سرویس ===== #
        product = self.service.create_product_shell(request.user, serializer.validated_data)
        
        return Response(ProductShellSerializer(product).data, status=status.HTTP_201_CREATED)

    # ===== تنظیمات قیمت دهی ===== #
    @extend_schema(request=ProductPricingConfigSerializer, responses=ProductPricingConfigSerializer)
    @action(detail=True, methods=['put', 'patch'], url_path='config')
    def pricing_config(self, request, pk=None):
        """ آپدیت تنظیمات قیمت‌گذاری محصول """
        serializer = ProductPricingConfigSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        
        config = self.service.update_pricing_config(pk, serializer.validated_data)
        return Response(ProductPricingConfigSerializer(config).data)

    # ===== جنس ها ===== #
    @extend_schema(request=MaterialSyncSerializer, summary="همگام‌سازی متریال‌ها")
    @action(detail=True, methods=['post'], url_path='sync-materials')
    def sync_materials(self, request, pk=None):
        serializer = MaterialSyncSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        self.service.sync_materials(
            product_id=pk,
            user=request.user,
            material_ids=serializer.validated_data['material_ids'],
            default_material_id=serializer.validated_data.get('default_material_id')
        )
        return Response({'status': 'Materials synced successfully'})

    # ===== تیراژهای ایجاد شده ===== #
    @extend_schema(request=QuantitySyncSerializer, summary="همگام‌سازی تیراژها")
    @action(detail=True, methods=['post'], url_path='sync-quantities')
    def sync_quantities(self, request, pk=None):
        serializer = QuantitySyncSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        self.service.sync_quantities(
            product_id=pk,
            user=request.user,
            quantity_ids=serializer.validated_data['quantity_ids']
        )
        return Response({'status': 'Quantities synced successfully'})

    # ===== Step 4: Add Option ===== #
    @extend_schema(request=OptionAttachWithPriceSerializer, summary="افزودن ویژگی به محصول")
    @action(detail=True, methods=['post'], url_path='attach-option')
    def attach_option(self, request, pk=None):
        serializer = OptionAttachWithPriceSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        self.service.attach_option_with_config(
            product_id=pk,
            data=serializer.validated_data
        )
        return Response({'status': 'Option attached with prices'}, status=status.HTTP_201_CREATED)
    
    # ===== Step 5: Update Option Prices ===== #
    @extend_schema(
        request=OptionPriceUpdateSerializer, 
        summary="بروزرسانی قیمت‌های مقادیر یک آپشن",
        description="لیستی از مقادیر به همراه قیمت جدید را می‌گیرد و یکجا آپدیت می‌کند."
    )
    @action(detail=True, methods=['post'], url_path='update-option-prices')
    def update_option_prices(self, request, pk=None):
        serializer = OptionPriceUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        data = serializer.validated_data
        
        try:
            self.service.update_option_values_pricing(
                product_id=pk,
                product_option_id=data['product_option_id'],
                updates=data['values']
            )
            return Response({'status': 'Prices updated successfully'}, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
    @extend_schema(
        request=FileRequirementSyncSerializer, 
        summary="تعیین فایل‌های مورد نیاز محصول"
    )
    @action(detail=True, methods=['post'], url_path='sync-files')
    def sync_files(self, request, pk=None):
        serializer = FileRequirementSyncSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        self.service.sync_file_requirements(
            product_id=pk,
            requirements=serializer.validated_data['requirements']
        )
        return Response({'status': 'File requirements updated successfully'})
