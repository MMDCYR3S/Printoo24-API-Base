from typing import Dict, Any, List, Optional
from django.db import transaction
from django.db.models import QuerySet

from ..models import ProductCategory, Product
from ..exceptions import ProductCategoryNotFoundException

# ========== CATEGORY SERVICE ========== #
class ProductCategoryService:
    """
    سرویس دامنه دسته‌بندی محصولات.
    """
    
    # ===== Read Operations ===== #
    def get_root_categories(self) -> QuerySet[ProductCategory]:
        """
        دریافت فقط دسته‌بندی‌های والد (ریشه) که فعال هستند.
        """
        return ProductCategory.objects.get_root_categories()
    
    def get_category_tree_queryset(self) -> QuerySet[ProductCategory]:
        """
        فقط کوئری‌ست را برمی‌گرداند. تبدیل به درخت وظیفه لایه نمایش است.
        """
        return ProductCategory.objects.get_all_active_categories()

    def get_all_active_categories(self):
        """ دریافت تمامی دسته‌های فعال """
        return ProductCategory.objects.get_all_active_categories()
    
    def get_all_subcategories_with_parent(self) -> QuerySet[ProductCategory]:
        """
        دریافت تمام زیردسته‌های فعال به همراه اطلاعات والد.
        این متد فقط داده خام (QuerySet) برمی‌گرداند.
        """
        return ProductCategory.objects.get_subcategories_with_parent()


    def get_category_by_slug(self, slug: str) -> Optional[ProductCategory]:
        """
        دریافت دسته‌بندی با اسلاگ (رایز کردن اکسپشن یا بازگرداندن None).
        در منیجر ما رایز می‌کند، اینجا هندل می‌کنیم تا سرویس اپلیکیشن بتونه None بگیره اگه خواست.
        """
        try:
            return ProductCategory.objects.get_by_slug(slug)
        except ProductCategoryNotFoundException:
            # در کد سرویس اپلیکیشن شما انتظار None دارد (if not category: return None)
            # پس اینجا اکسپشن را می‌گیریم و None برمی‌گردانیم
            return None

    def get_category_descendants_ids(self, slug: str) -> List[int]:
        """
        دریافت لیست شناسه‌های فرزندان برای فیلتر کردن محصولات.
        """
        try:
            category = ProductCategory.objects.get_by_slug(slug)
            return list(category.get_descendants(include_self=True).values_list('id', flat=True))
        except ProductCategoryNotFoundException:
            return []

    # ===== Write Operations ===== #
    @transaction.atomic
    def create_category(self, data: Dict[str, Any]) -> ProductCategory:
        """
        ایجاد یک دسته‌بندی جدید.
        """
        category = ProductCategory(**data)
        category.full_clean()
        category.save()
        return category

    @transaction.atomic
    def update_category(self, instance: ProductCategory, data: Dict[str, Any]) -> ProductCategory:
        """
        ویرایش دسته‌بندی.
        """
        for field, value in data.items():
            setattr(instance, field, value)
        instance.full_clean()
        instance.save()
        return instance

    def delete_category(self, instance: ProductCategory) -> None:
        """
        حذف یک دسته‌بندی.
        """
        instance.delete()

    # ===== Bulk Operations ===== #
    @transaction.atomic
    def bulk_toggle_status(self, ids: List[int], is_active: bool) -> int:
        return ProductCategory.objects.bulk_toggle_status(ids, is_active)

    @transaction.atomic
    def bulk_delete(self, ids: List[int]) -> tuple:
        return ProductCategory.objects.bulk_delete_categories(ids)

    def get_products_by_category_ids(self, category_ids: List[int]) -> QuerySet[Product]:
        """
        دریافت محصولات بر اساس لیستی از شناسه‌های دسته‌بندی.
        * اصلاح شده برای ساختار M2M *
        """
        return Product.objects.filter(
            is_active=True,
            categories__id__in=category_ids
        ).select_related(
            'pricing_config'
        ).distinct()

    # ===== UPSERT METHOD ===== #
    @transaction.atomic
    def bulk_upsert_categories(self, payload_data: List[Dict[str, Any]], user) -> List[Dict]:
        """
        عملیات ترکیبی ایجاد و ویرایش گروهی دسته‌بندی‌ها (اصلاح شده).
        """
        
        updates_data = [item for item in payload_data if item.get('id')]
        creates_data = [item for item in payload_data if not item.get('id')]

        results = []
        
        # ===== بخش ویرایش (Updates) ===== #
        update_ids = [item['id'] for item in updates_data]
        existing_categories_map = {
            cat.id: cat 
            for cat in ProductCategory.objects.filter(id__in=update_ids)
        }

        for item in updates_data:
            # ===== اصلاح: حذف فیلدهای مجازی از دیکشنری ===== #
            pk_id = item.pop('id') 
            parent_slug = item.pop('parent_slug', None)
            
            instance = existing_categories_map.get(pk_id)
            if not instance:
                continue 

            if parent_slug:
                parent = ProductCategory.objects.filter(slug=parent_slug).first()
                instance.parent = parent
            elif parent_slug == "": 
                instance.parent = None

            for field, value in item.items():
                if hasattr(instance, field):
                    setattr(instance, field, value)
            
            instance.full_clean()
            instance.save() 
            results.append({"status": "updated", "id": instance.id, "name": instance.name})

        # ===== بخش ایجاد (Creates) ===== #
        roots = [c for c in creates_data if not c.get('parent_slug')]
        children = [c for c in creates_data if c.get('parent_slug')]
        
        created_map = {} 

        # ===== ایجاد دسته بندی های اصلی ===== #
        for item in roots:
            # ===== اصلاح: حذف فیلدهای مجازی ===== #
            parent_slug = item.pop('parent_slug', None)
            
            item['user'] = user
            instance = ProductCategory(**item)
            instance.full_clean()
            instance.save()
            created_map[instance.slug] = instance
            results.append({"status": "created", "id": instance.id, "name": instance.name})

        # ===== ایجاد زیردسته ===== #
        attempts = 0
        while children and attempts < 5:
            remaining_children = []
            for item in children:
                # ===== اصلاح: حذف فیلدهای مجازی ===== #
                parent_slug = item.pop('parent_slug', None)
                
                # جستجوی والد (ابتدا در حافظه سپس در دیتابیس)
                parent = created_map.get(parent_slug) or ProductCategory.objects.filter(slug=parent_slug).first()
                
                if parent:
                    item['parent'] = parent
                    item['user'] = user
                    instance = ProductCategory(**item)
                    instance.full_clean()
                    instance.save()
                    created_map[instance.slug] = instance
                    results.append({"status": "created", "id": instance.id, "name": instance.name})
                else:
                    remaining_children.append(item)
            
            children = remaining_children
            attempts += 1

        return results
