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
    # ===== UPSERT METHOD (OPTIMIZED) ===== #
    @transaction.atomic
    def bulk_upsert_categories(self, validated_data_list: List[Dict[str, Any]], user) -> List[Dict]:
        """
        عملیات ترکیبی ایجاد و ویرایش گروهی دسته‌بندی‌ها.
        پشتیبانی از تمامی فیلدها (عکس، توضیحات و ...).
        """
        results = []
        
        # تفکیک داده‌ها
        updates_data = [item for item in validated_data_list if item.get('id')]
        creates_data = [item for item in validated_data_list if not item.get('id')]

        # ====================================
        # 1. پردازش ویرایش‌ها (Updates)
        # ====================================
        if updates_data:
            update_ids = [item['id'] for item in updates_data]
            # واکشی دسته‌ها برای آپدیت
            existing_categories = ProductCategory.objects.filter(id__in=update_ids)
            existing_map = {cat.id: cat for cat in existing_categories}

            for item in updates_data:
                pk = item.pop('id')
                instance = existing_map.get(pk)
                if not instance:
                    continue
                
                # مدیریت والد (Parent)
                # اگر parent_slug در دیکشنری بود (حتی اگر None بود یعنی والد حذف شود)
                if 'parent_slug' in item:
                    p_slug = item.pop('parent_slug')
                    if p_slug:
                        parent = ProductCategory.objects.filter(slug=p_slug).first()
                        instance.parent = parent
                    else:
                        instance.parent = None # قطع رابطه والد

                # ===== آپدیت ===== #
                for field, value in item.items():
                    # ===== ست کردن فیلد‌هایی که در مدل هستند ===== #
                    if hasattr(instance, field):
                        setattr(instance, field, value)
                
                instance.full_clean()
                instance.save()
                results.append({"status": "updated", "id": instance.id, "name": instance.name})

        # ===== INSERT OPERATIONS ===== #
        created_slug_map = {} 

        # ===== ایجاد والد قبل از فرزند ===== #
        pending_creates = creates_data
        attempts = 0
        max_attempts = 10

        while pending_creates and attempts < max_attempts:
            next_pending = []
            for item in pending_creates:
                parent_slug = item.pop('parent_slug', None)
                
                parent = None
                can_create = True

                if parent_slug:
                    if parent_slug in created_slug_map:
                        parent = created_slug_map[parent_slug]
                    else:
                        parent = ProductCategory.objects.filter(slug=parent_slug).first()
                        if not parent:
                            item['parent_slug'] = parent_slug
                            next_pending.append(item)
                            can_create = False
                
                if can_create:
                    item['parent'] = parent
                    item['user'] = user
                    
                    instance = ProductCategory(**item)
                    instance.full_clean()
                    instance.save()
                    
                    created_slug_map[instance.slug] = instance
                    results.append({"status": "created", "id": instance.id, "name": instance.name})
            
            if len(pending_creates) == len(next_pending) and pending_creates:
                pass 
            
            pending_creates = next_pending
            attempts += 1

        return results
