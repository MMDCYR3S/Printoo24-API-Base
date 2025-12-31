import logging

from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist

from core.models import User
from apps.cart.models import Cart, CartItem

# ===== تعریف لاگرهای اختصاصی با پیشوند cart ===== #
logger_list = logging.getLogger('cart.services.list')
logger_detail = logging.getLogger('cart.services.detail')

# ===== Cart List Service ===== #
class CartListService:
    """
    سرویس مدیریت نمایش لیست آیتم‌های سبد خرید (Guest + User).
    """

    def get_cart_details(self, user: User = None, session_key: str = None) -> dict:
        """
        دریافت سبد خرید و آیتم‌ها بر اساس کاربر یا سشن.
        """
        identifier = f"User:{user.id}" if user else f"Session:{session_key}"
        logger_list.info(f"Fetching cart list for {identifier}")
        
        cart = None
        if user and user.is_authenticated:
            cart = Cart.objects.filter(user=user).first()
        elif session_key:
            cart = Cart.objects.filter(session_key=session_key, user__isnull=True).first()

        # ===== اگر کاربر یا سشن وجود نداشته باشد، سپس بازگشت خالی ===== #
        if not cart:
            return {
                "cart": None,
                "items": [],
                "summary": {"total_price": 0}
            }            
        # ===== دریافت آیتم‌ها ===== #
        items = CartItem.objects.filter(cart=cart).select_related('product').prefetch_related('uploads')
        
        # ===== محاسبه جمع قیمت ===== #
        total_price = sum(item.price for item in items)
        
        # ===== بازگشت ===== #
        return {
            "cart": cart,
            "items": items,
            "summary": {
                "total_price": total_price
            }
        }

# ======= Cart Item Detail Service ======= #
class CartItemDetailService:
    """
    سرویس نمایش جزئیات یک آیتم خاص با بررسی مالکیت (Guest + User).
    """
        
    def get_item_detail(self, item_id: int, user: User = None, session_key: str = None) -> CartItem:
        """
        دریافت جزئیات آیتم با بررسی دقیق دسترسی.
        """
        logger_detail.info(f"Fetching item {item_id}")
        
        # ===== اگر کاربر یا سشن وجود نداشته باشد ===== #
        if not user and not session_key:
             raise ObjectDoesNotExist("شناسه معتبری برای یافتن آیتم وجود ندارد.")
        
        # ===== دریافت آیتم ===== # 
        query = Q(id=item_id)
        if user and user.is_authenticated:
            query &= Q(cart__user=user)
        else:
            query &= Q(cart__session_key=session_key, cart__user__isnull=True)
         
        # ===== دریافت ===== #
        try:
            item = CartItem.objects.select_related('product').prefetch_related('uploads').get(query)
            return item
            
        except CartItem.DoesNotExist:
            logger_detail.warning(f"Access denied or not found: Item {item_id}")
            raise ObjectDoesNotExist("آیتم مورد نظر یافت نشد.")
         