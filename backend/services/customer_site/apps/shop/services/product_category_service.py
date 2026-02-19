import logging
from typing import List, Dict, Any, Optional
from mptt.utils import get_cached_trees
from django.shortcuts import get_object_or_404
from rest_framework.reverse import reverse
from django.urls import NoReverseMatch

from core.product.services import ProductCategoryService, ProductService
from core.models import ProductCategory
from api.v1.dashboard.serializers import ProductMinimalSerializer

logger = logging.getLogger('shop.services.category')

# ===== Shop Category Service ===== #
class ShopCategoryService:
    """
    سرویس اپلیکیشن برای مدیریت نمایش دسته‌بندی‌ها (منو و صفحه لندینگ).
    """
    def __init__(self, request=None):
        self.request = request
        self._domain_service = ProductCategoryService()
        self._product_repo = ProductService()
        
    # ===== Get Category Tree Structure ===== #
    def get_category_tree_structure(self, include_products: bool = False) -> List[Dict[str, Any]]:
        """
        خروجی: ساختار درختی.
        """
        categories = self._domain_service.get_category_tree_queryset()
        root_nodes = get_cached_trees(categories)
        return [self._serialize_node_light(node, include_products) for node in root_nodes]

    def _serialize_node_light(self, node: ProductCategory, include_products: bool = False) -> Dict[str, Any]:
        """تبدیل نود به دیکشنری سبک"""
        children = [self._serialize_node_light(child, include_products) for child in node.get_children()]
        
        data = {
            "id": node.id,
            "name": node.name,
            "slug": node.slug,
            "has_children": len(children) > 0,
            "thumbnail": self._get_image_url(node.banner_box),
            "links": {
                "products_url": self._generate_product_filter_url(node.slug),
                "landing_url": self._generate_category_landing_url(node.slug)
            },
            "children": children,
        }
        
        # ===== اگر باید محصولات هم بازنشون شود ===== #
        if include_products:
            products_qs = self._product_repo.get_products_by_category_ids([node.id])[:7]
            data["products"] = ProductMinimalSerializer(
                products_qs, 
                many=True, 
                context={'request': self.request}
            ).data

        return data

    # ===== Get Category Landing Data ===== #
    def get_category_landing_data(self, slug: str) -> Dict[str, Any]:
        """
        خروجی: اطلاعات کامل یک دسته برای نمایش در صفحه اختصاصی.
        شامل: بنرها، توضیحات و لیست محصولات (خودش + زیرمجموعه‌ها).
        """
        logger.info(f"Fetching landing data for category: {slug}")
        
        # ===== دریافت دسته‌بندی ===== #
        category = self._domain_service.get_category_by_slug(slug)
        if not category:
            return None
        
        descendant_ids = self._domain_service.get_category_descendants_ids(slug)

        products_queryset = self._product_repo.get_products_by_category_ids(descendant_ids)[:7]
        # ===== دریافت محصولات ===== #
        breadcrumbs = [
                {"name": ancestor.name, "slug": ancestor.slug} 
                for ancestor in category.get_ancestors(include_self=False)
            ]

        # ===== ساخت دیکشنری ===== #
        data = {
                "category_info": {
                    "id": category.id,
                    "name": category.name,
                    "slug": category.slug,
                    "description": category.description,
                    "breadcrumbs": breadcrumbs,
                    "banners": {
                        "wide": self._get_image_url(category.banner_wide),
                        "box": self._get_image_url(category.banner_box),
                    }
                },
                "sub_categories": [
                    {
                        "id": child.id,
                        "name": child.name, 
                        "slug": child.slug, 
                        "thumbnail": self._get_image_url(child.banner_box),
                        "link": self._generate_product_filter_url(child.slug)
                    } 
                    for child in category.get_children() if child.is_active
                ],
                "products": ProductMinimalSerializer(
                    products_queryset, 
                    many=True, 
                    context={'request': self.request}
                ).data
            }
        return data
    
    # ===== Get All Categories With Products ===== #
    def get_all_categories_with_products(self) -> List[Dict[str, Any]]:
        """
        دریافت لیست تمام دسته‌بندی‌های اصلی (Root) به همراه محصولات.
        """
        logger.info("Fetching all root categories with products")

        root_categories = self._domain_service.get_root_categories()
        result_list = []

        for category in root_categories:
            descendants = category.get_descendants(include_self=True)
            descendant_ids = descendants.values_list('id', flat=True)

            products_queryset = self._product_repo.get_products_by_category_ids(descendant_ids)
            products_queryset = products_queryset.prefetch_related('product_image')[:7]

            category_data = {
                "category_info": {
                    "id": category.id,
                    "name": category.name,
                    "slug": category.slug,
                    "banners": {
                        "wide": self._get_image_url(category.banner_wide),
                        "box": self._get_image_url(category.banner_box),
                    }
                },
                "sub_categories": [
                    {
                        "id": child.id,
                        "name": child.name, 
                        "slug": child.slug,
                        "thumbnail": self._get_image_url(child.banner_box),
                        "link": self._generate_product_filter_url(child.slug)
                    } 
                    for child in category.get_children() if child.is_active
                ],
                "products": products_queryset 
            }
            result_list.append(category_data)
            
        return result_list
    
    def get_subcategories_flat_list(self) -> List[Dict[str, Any]]:
        """
        دریافت لیست مسطح از تمام زیردسته‌ها به همراه نام والد.
        مناسب برای نمایش در لیست‌های فیلتر یا نقشه سایت.
        """
        logger.info("Fetching flat list of subcategories with parents")
        # ===== دریافت تمامی زیردسته بندی ها ===== #
        categories = self._domain_service.get_all_subcategories_with_parent()
        
        result = []
        
        # ===== ایجاد یک والد برای هر زیر‌دسته ===== #
        for cat in categories:
            parent_data = None
            if cat.parent:
                parent_data = {
                    "id": cat.parent.id,
                    "name": cat.parent.name,
                    "slug": cat.parent.slug
                }
                
            products_qs = self._product_repo.get_products_by_category_ids([cat.id])[:7]
                
            result.append({
                "id": cat.id,
                "name": cat.name,
                "slug": cat.slug,
                "description": cat.description,
                "is_active": cat.is_active,
                "banners": {
                    "wide": self._get_image_url(cat.banner_wide),
                    "box": self._get_image_url(cat.banner_box),
                },
                "parent": parent_data,
                "products": products_qs
            })
            
        return result

    # ===== Get Image URL ===== #
    def _get_image_url(self, image_field):
        """تولید آدرس کامل تصویر"""
        if not image_field: 
            return None
        try:
            if self.request:
                return self.request.build_absolute_uri(image_field.url)
            return image_field.url
        except Exception as e:
            logger.warning(f"Error generating image URL: {e}")
            return None

    def _generate_product_filter_url(self, slug: str) -> Optional[str]:
        """لینک لیست محصولات فیلتر شده بر اساس دسته"""
        if not self.request: return None
        try:
            base_url = reverse("api:v1:shop:product-list", request=self.request)
            return f"{base_url}?category={slug}"
        except NoReverseMatch:
            logger.error("Reverse match failed for product-list")
            return None

    def _generate_category_landing_url(self, slug: str) -> Optional[str]:
        """لینک صفحه اختصاصی دسته"""
        if not self.request: return None
        try:
            return reverse("api:v1:shop:category-landing", kwargs={'slug': slug}, request=self.request)
        except NoReverseMatch:
            return None
