from typing import Dict, Any, List, Optional
from django.db import transaction
from django.db.models import QuerySet

from ..models import ProductCategory, Product
from ..exceptions import ProductCategoryNotFoundException, ProductCategoryHasDependencyException
from django.db.models import ProtectedError
from celery import current_app

try:
    from apps.shop.tasks import compress_category_images_task
except ImportError:
    compress_category_images_task = None


# ========== CATEGORY SERVICE ========== #
class ProductCategoryService:
    """
    سرویس دامنه دسته‌بندی محصولات.
    """
    
    # ===== Read Operations ===== #
    def get_root_categories(self, active_only=False):
        """
        دریافت دسته‌بندی‌های والد (ریشه).
        active_only: برای داشبورد False، برای فرانت True
        """
        return ProductCategory.objects.get_root_categories(active_only=active_only)
    
    def get_category_tree_queryset(self) -> QuerySet[ProductCategory]:
        """
        فقط کوئری‌ست را برمی‌گرداند. تبدیل به درخت وظیفه لایه نمایش است.
        """
        return ProductCategory.objects.get_all_active_categories()
    
    def get_all_category_tree_queryset(self) -> QuerySet[ProductCategory]:
        """
        فقط کوئری‌ست را برمی‌گرداند. تبدیل به درخت وظیفه لایه نمایش است.
        """
        return ProductCategory.objects.get_all_categories()

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
        category = ProductCategory(**data)
        category.full_clean()
        category.save()

        if category.banner_wide or category.banner_box:
            category_id = category.id
            def _queue_compress():
                current_app.send_task(
                    'compress_category_images_task',
                    args=[category_id]
                )
            transaction.on_commit(_queue_compress)

        return category

    @transaction.atomic
    def update_category(self, instance: ProductCategory, data: Dict[str, Any]) -> ProductCategory:
        image_fields_changed = 'banner_wide' in data or 'banner_box' in data

        for field, value in data.items():
            setattr(instance, field, value)
        instance.full_clean()
        instance.save()

        if image_fields_changed and (instance.banner_wide or instance.banner_box):
            category_id = instance.id
            def _queue_compress():
                current_app.send_task(
                    'compress_category_images_task',
                    args=[category_id]
                )
            transaction.on_commit(_queue_compress)

        return instance

    def delete_category(self, instance: ProductCategory) -> None:
        try:
            instance.delete()
        except ProtectedError:
            raise ProductCategoryHasDependencyException("دسته‌بندی قابل حذف نیست، چون وابستگی‌هایی دارد.")


    # ===== Bulk Operations ===== #
    @transaction.atomic
    def bulk_toggle_status(self, ids: List[int], is_active: bool) -> int:
        return ProductCategory.objects.bulk_toggle_status(ids, is_active)

    @transaction.atomic
    def bulk_delete(self, ids: List[int]) -> tuple:
        try:
            return ProductCategory.objects.bulk_delete_categories(ids)
        except ProtectedError:
            raise ProductCategoryHasDependencyException("برخی دسته‌بندی‌ها قابل حذف نیستند چون وابستگی دارند.")\
                
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
    def bulk_upsert_categories(self, validated_data_list: List[Dict[str, Any]], user) -> List[Dict]:
        """
        عملیات ترکیبی ایجاد و ویرایش گروهی دسته‌بندی‌ها.
        پشتیبانی از تمامی فیلدها (عکس، توضیحات و ...).
        """
        with ProductCategory.objects.delay_mptt_updates():
            results = []
            ids_to_compress = []
            
            updates_data = [item for item in validated_data_list if item.get('id')]
            creates_data = [item for item in validated_data_list if not item.get('id')]

            # ===== UPDATE OPERATION ===== #
            if updates_data:
                update_ids = [item['id'] for item in updates_data]
                # ===== واکشی داده‌های مربوط به والد ===== #
                existing_categories = ProductCategory.objects.filter(id__in=update_ids)
                existing_map = {cat.id: cat for cat in existing_categories}

                for item in updates_data:
                    pk = item.pop('id')
                    instance = existing_map.get(pk)
                    if not instance:
                        continue
                    
                    # ===== بررسی تغییر فیلدهای عکس ===== #
                    image_fields_changed = 'banner_wide' in item or 'banner_box' in item
                    
                    # ===== مدیریت تغییر والد در آپدیت ===== #
                    if 'parent_slug' in item:
                        p_slug = item.pop('parent_slug')
                        if p_slug:
                            parent = ProductCategory.objects.filter(slug=p_slug).first()
                            instance.parent = parent
                        else:
                            instance.parent = None  # قطع رابطه والد

                    # ===== آپدیت ===== #
                    for field, value in item.items():
                        # ===== ست کردن فیلد‌هایی که در مدل هستند ===== #
                        if hasattr(instance, field):
                            setattr(instance, field, value)
                    
                    instance.full_clean()
                    instance.save()
                    results.append({"status": "updated", "id": instance.id, "name": instance.name})

                    # ===== اضافه کردن به لیست فشرده‌سازی در صورت تغییر عکس ===== #
                    if image_fields_changed and (instance.banner_wide or instance.banner_box):
                        ids_to_compress.append(instance.id)

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

                        # ===== اضافه کردن به لیست فشرده‌سازی در صورت وجود عکس ===== #
                        if instance.banner_wide or instance.banner_box:
                            ids_to_compress.append(instance.id)
                
                if len(pending_creates) == len(next_pending) and pending_creates:
                    pass
                
                pending_creates = next_pending
                attempts += 1

            # ===== queue فشرده‌سازی بعد از commit کامل transaction ===== #
            if ids_to_compress:
                ids_snapshot = list(ids_to_compress)
                def _queue_compress():
                    for cat_id in ids_snapshot:
                        current_app.send_task(
                            'compress_category_images_task',
                            args=[cat_id]
                        )
                transaction.on_commit(_queue_compress)

        return results
