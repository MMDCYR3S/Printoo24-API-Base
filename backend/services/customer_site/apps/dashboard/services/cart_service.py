import logging
from typing import Dict, Any

from django.db import transaction
from django.db.models import Count, Sum, F, Prefetch
from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError

from core.models import User, Product
from apps.cart.models import Cart, CartItem


from apps.cart.services.add_to_cart_service import AddToCartService
from apps.cart.services.update_cart_service import CartItemUpdateService
from apps.cart.services.delete_cart_service import CartItemDeleteService, CartClearService

# ===== Logger ===== #
logger = logging.getLogger("dashboard.services.cart_dashboard")

# ===== Cart Dashboard Service ===== #
class CartDashboardService:
    """
    سرویس مدیریت سبد خرید مخصوص پنل ادمین.
    نقش: این سرویس به عنوان یک Wrapper/Adapter عمل می‌کند تا سرویس‌های اصلی
    را با نیازهای پنل ادمین هماهنگ کند.
    """

    def get_all_carts_queryset(self):
        """
        دریافت لیست تمام سبدها برای جدول داشبورد.
        """
        return Cart.objects.select_related('user').prefetch_related(
            'cart_items'
        ).annotate(
            items_count=Count('cart_items'),
            total_amount=Sum(F('cart_items__price'))
        ).order_by('-updated_at')

    def get_user_cart_details(self, cart_id: int):
        """ دریافت جزئیات کامل سبد خرید برای نمایش در ادمین """
        logger.info(f"START: Get Cart Details for User ID {cart_id}")
        # ===== دریافت سبد خرید ===== #
        cart = get_object_or_404(
            Cart.objects.prefetch_related(
                Prefetch(
                    'cart_items',
                    queryset=CartItem.objects.select_related('product').prefetch_related(
                        'uploads'
                    )
                )
            ).select_related('user'),
            pk=cart_id
        )

        return {
            'cart': cart,
            'user': cart.user,
            'session_key': cart.session_key
        }

    # ===== Write Operations (Commands) ===== #
    @transaction.atomic
    def add_item_to_cart(self, cart_id: int, data: Dict[str, Any]):
        """
        افزودن آیتم توسط ادمین به یک سبد خرید خاص.
        """
        logger.info(f"Admin adding item for Cart ID {cart_id}")
        
        # ===== دریافت سبد خرید ===== #
        cart = get_object_or_404(Cart, pk=cart_id)
        
        # ===== دریافت محصول ===== #
        product_slug = data.get('product_slug')
        if not product_slug:
            raise ValidationError("شناسه محصول (Slug) الزامی است.")
            
        product = get_object_or_404(Product, slug=product_slug)

        selections = self._map_admin_data_to_selections(data)
        
        service = AddToCartService(user=cart.user, session_key=cart.session_key)
        try:
            cart_item = service.execute(
                product_id=product.id,
                selections=selections
            )
            logger.info(f"Item {cart_item.id} added via Admin to Cart {cart_id}.")
            return cart_item
        except Exception as e:
            logger.error(f"Failed to add item via Admin: {e}")
            raise e

    @transaction.atomic
    def update_cart_item(self, cart_id: int, item_id: int, data: Dict[str, Any]):
        """ ویرایش آیتم توسط ادمین در یک سبد خاص """
        logger.info(f"Admin updating Item {item_id} in Cart {cart_id}") 

        # ===== دریافت سبد خرید ===== #
        cart = get_object_or_404(Cart, pk=cart_id)
        
        selections = self._map_admin_data_to_selections(data)

        service = CartItemUpdateService(user=cart.user, session_key=cart.session_key)
        try:
            updated_item = service.update(
                cart_item_id=item_id,
                raw_data=selections
            )
            return updated_item
        except Exception as e:
            logger.error(f"Failed to update item via Admin: {e}")
            raise e

    def remove_item_from_cart(self, cart_id: int, item_id: int):
        """ حذف آیتم از یک سبد خاص """
        cart = get_object_or_404(Cart, pk=cart_id)
        service = CartItemDeleteService(user=cart.user, session_key=cart.session_key)
        service.delete(item_id)

    def clear_cart(self, cart_id: int):
        """ خالی کردن کل یک سبد خرید """
        cart = get_object_or_404(Cart, pk=cart_id)
        service = CartClearService(user=cart.user, session_key=cart.session_key)
        service.clear()

    # ===== Helper Methods (Mapper) ===== #
    def _map_admin_data_to_selections(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        این متد حیاتی است!
        داده‌های ورودی از فرم ادمین را به ساختار استاندارد selections
        که CartProcessor انتظار دارد تبدیل می‌کند.
        
        فرض بر این است که ادمین دیتا را این شکلی می‌فرستد:
        {
            'quantity': 1000,
            'selections': {  <-- یا شاید فیلدها فلت باشند، اینجا نرمال‌سازی می‌کنیم
                'size_id': 5,
                'width': 10,
                'options': {'12': 'PaperType', ...}
            }
        }
        """
        if 'selections' in data and isinstance(data['selections'], dict):
            final_selections = data['selections'].copy()
            if 'quantity' in data:
                final_selections['quantity'] = data['quantity']
            return final_selections

        selections = {}

        direct_fields = ['quantity', 'size_id', 'quantity_id', 'width', 'height', 'has_design', 'name', 'description']
        for field in direct_fields:
            if field in data:
                selections[field] = data[field]

        if 'options' in data:
            selections['options'] = data['options']
            
        return selections
