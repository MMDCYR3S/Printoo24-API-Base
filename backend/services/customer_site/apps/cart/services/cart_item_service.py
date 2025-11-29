import logging
from django.core.exceptions import ObjectDoesNotExist

from core.models import User, CartItem
from core.domain.cart.services import CartDomainService
from core.domain.cart.repositories import CartItemRepository

# ===== تعریف لاگرهای اختصاصی با پیشوند cart ===== #
logger_list = logging.getLogger('cart.services.list')
logger_detail = logging.getLogger('cart.services.detail')

# ===== Cart List Service ===== #
class CartListService:
    """
    سرویس مدیریت نمایش لیست آیتم‌های سبد خرید کاربر.
    
    این سرویس وظیفه دارد سبد خرید کاربر را بازیابی کرده (یا بسازد)
    و تمام آیتم‌های موجود در آن را برای نمایش در فرانت‌اند آماده کند.
    """
    
    def __init__(self
        ):
        # ===== تزریق وابستگی‌ها ===== #
        self._domain_service = CartDomainService()
        
    def get_user_cart_items(self, user: User) -> dict:
        """
        دریافت سبد خرید و لیست آیتم‌های آن.

        Args:
            user (User): کاربر درخواست دهنده.

        Returns:
            dict: دیکشنری شامل آبجکت سبد خرید و لیست کوئری‌ست آیتم‌ها.
        """
        logger_list.info(f"Fetching cart list for User ID: {user.id}")
        
        try:
            # ===== دریافت یا ایجاد سبد خرید ===== #
            cart = self._domain_service.get_or_create_cart_for_user(user)
            logger_list.debug(f"Cart retrieved/created for User ID: {user.id}, Cart ID: {cart.id}")
            
            # ===== دریافت آیتم‌های سبد خرید ===== #
            items = self._domain_service.get_item_details(cart)
            logger_list.info(f"Retrieved {items.count()} items for Cart ID: {cart.id}")
            
            # ===== محاسبه مجموع قیمت کل سبد خرید ===== #
            total_price = sum(item.price for item in items)
            
            return {
                "cart": cart,
                "items": items,
                "summary": {
                    "total_price": total_price,
                    "item_count": items.count()
                }
            }
        except Exception as e:
            logger_list.exception(f"Error fetching cart list for User ID: {user.id}")
            raise e

# ======= Cart Item Detail Service ======= #
class CartItemDetailService:
    """
    سرویس مدیریت نمایش جزئیات یک آیتم خاص در سبد خرید.
    
    این سرویس برای زمانی استفاده می‌شود که کاربر می‌خواهد جزئیات یک محصول خاص
    در سبد خرید خود (مثل فایل‌های آپلود شده یا ویژگی‌های انتخابی) را مشاهده یا ویرایش کند.
    """
    
    def __init__(self):
        # ===== تزریق وابستگی‌ها ===== #
        self._item_repo = CartItemRepository()
        
    def get_item_detail(self, item_id: int, user: User) -> CartItem:
        """
        دریافت جزئیات یک آیتم مشخص با بررسی مالکیت.

        Args:
            item_id (int): شناسه آیتم سبد خرید.
            user (User): کاربر درخواست دهنده (جهت احراز مالکیت).

        Returns:
            CartItem: آبجکت آیتم پیدا شده.

        Raises:
            ObjectDoesNotExist: اگر آیتم پیدا نشود یا متعلق به کاربر نباشد.
        """
        logger_detail.info(f"Fetching details for CartItem ID: {item_id}, User ID: {user.id}")
        
        try:
            item = self._item_repo.get_item_details(item_id=item_id, user=user)

            if not item:
                logger_detail.warning(f"CartItem {item_id} not found or access denied for User ID: {user.id}")
                raise ObjectDoesNotExist("آیتم مورد نظر یافت نشد یا متعلق به شما نیست.")
            
            logger_detail.debug(f"CartItem {item_id} details retrieved successfully.")
            return item
            
        except ObjectDoesNotExist as e:
            raise e
        except Exception as e:
            logger_detail.exception(f"Unexpected error retrieving CartItem {item_id} for User ID: {user.id}")
            raise e
