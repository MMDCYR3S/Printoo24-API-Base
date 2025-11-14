from rest_framework.generics import GenericAPIView
from rest_framework import status
from drf_spectacular.utils import extend_schema

from ..serializers import PriceCalculationInputSerializer
from apps.shop.services import ProductPriceCalculator

# ====== Calculate Price View ====== #
@extend_schema(tags=["Product"])
class CalculatePriceView(GenericAPIView):
    """
    API View اختصاصی برای محاسبه قیمت نهایی یک محصول بر اساس انتخاب‌های کاربر.
    این View فقط متد POST را می‌پذیرد.
    """
    serializer_class = PriceCalculationInputSerializer
    
    def post(self, request, *args, **kwargs):
        # ====== اعتبارسنجی داده‌های ورودی ====== #
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        validated_data = serializer.validated_data
        
        # ===== دریافت اطلاعات از سمت کاربر ===== #
        product = validated_data['product_id']
        quantity = validated_data['quantity_id']
        material = validated_data['material_id']
        size = validated_data.get('size_id')
        options = validated_data.get('option_ids', [])
        width = validated_data.get('width')
        height = validated_data.get('height')
        
        # ===== ایجاد سرویس برای محاسبه قیمت ===== #
        calculator = ProductPriceCalculator()
        
        # ===== تلاش برای محاسبه ===== #
        try:
            final_price = calculator.calculate(
                product=product,
                quantity=quantity,
                material=material,
                size=size,
                options=options,
                width=width,
                height=height
            )
            return Response({'final_price': final_price}, status=status.HTTP_200_OK)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
