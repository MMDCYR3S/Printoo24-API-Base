from rest_framework.generics import RetrieveAPIView
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema

from apps.shop.services import ShopProductDetailService
from ..serializers import ProductListSerializer, ProductDetailSerializer
from core.models import Product

# ====== Product Detail View ====== #
@extend_schema(
    tags=["Product"],
    description="API برای نمایش لیست محصولات همراه با فیلترینگ پیشرفته.",
)
class ProductDetailView(RetrieveAPIView):
    """
    API View برای نمایش جزئیات کامل یک محصول با تمام گزینه‌های قیمت‌گذاری.
    """
    serializer_class = ProductDetailSerializer
    lookup_field = 'slug'
    queryset = Product.objects.filter(is_active=True)

    def retrieve(self, request, *args, **kwargs):
        """
        این متد را override می‌کنیم تا از سرویس خودمان برای آماده‌سازی داده‌ها استفاده کنیم.
        """
        slug = self.kwargs.get(self.lookup_field)
        
        # ===== ایجاد سرویس برای دریافت اطلاعات پایه ===== #
        service = ShopProductDetailService()
        product_data_dict = service.get_product_detail_for_display(slug=slug)

        # ===== بررسی وجود محصول ===== #
        if product_data_dict is None:
            return Response({"detail": "محصول مورد نظر پیدا نشد."}, status=status.HTTP_404_NOT_FOUND)

        # ===== ساخت سریالایزر به واسطه داده های بازگشتی از سرویس ===== #
        serializer = self.get_serializer(product_data_dict)
        
        # ===== دریافت پاسخ نهایی ===== #
        return Response(serializer.data)