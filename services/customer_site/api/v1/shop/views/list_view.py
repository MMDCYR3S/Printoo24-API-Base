from rest_framework.generics import ListAPIView
from drf_spectacular.utils import extend_schema

from apps.shop.filters import ProductFilter
from ..serializers import ProductListSerializer 
from apps.shop.services import ShopProductListService

# ======= Product List View ======= #
@extend_schema(
    tags=["Product"],
    description="API برای نمایش لیست محصولات همراه با فیلترینگ پیشرفته.",
)
class ProductListView(ListAPIView):
    """
    API View برای نمایش لیست محصولات همراه با فیلترینگ پیشرفته.
    """
    serializer_class = ProductListSerializer
    filterset_class = ProductFilter
    
    def get_queryset(self):
        """
        متد اصلی برای دریافت کوئری‌ست.
        از سرویس لیست محصولات برای گرفتن کوئری‌ست پایه استفاده می‌کند.
        """
        # ====== دریافت سرویس لیست ====== #
        service = ShopProductListService()
        queryset = service.get_base_queryset()
        
        # ===== ایجاد فیلترینگ پیش فرض برای جلوگیری از تکرار داده ها ===== #
        filterset = self.filterset_class(self.request.GET, queryset=queryset)
        
        return filterset.qs.distinct()
