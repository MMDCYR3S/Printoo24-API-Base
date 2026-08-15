from typing import Optional
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.exceptions import NotFound

from core.models import User
from core.financial.models import Quotation
from apps.cart.models import Cart, CartItem


class CartQuotationService:
    """
    سرویس دریافت پیش‌فاکتورهای مرتبط با سبد خرید.
    """

    def get_cart_quotations(self, user: Optional[User] = None, session_key: Optional[str] = None):
        """
        دریافت لیست تمام پیش‌فاکتورهای سبد خرید.
        """
        if user and user.is_authenticated:
            cart = Cart.objects.filter(user=user).first()
        elif session_key:
            cart = Cart.objects.filter(session_key=session_key).first()
        else:
            cart = None

        if not cart:
            return Quotation.objects.none()

        return Quotation.objects.filter(
            cart_item__cart=cart,
            cart_item__isnull=False
        ).select_related(
            'cart_item__product', 'created_by'
        ).order_by('-created_at')

    def get_quotation_by_cart_item(
        self,
        cart_item_id: int,
        user: Optional[User] = None,
        session_key: Optional[str] = None,
    ) -> Quotation:
        """
        دریافت جزئیات پیش‌فاکتور بر اساس شناسه آیتم سبد خرید.
        """
        if user and user.is_authenticated:
            cart = Cart.objects.filter(user=user).first()
        elif session_key:
            cart = Cart.objects.filter(session_key=session_key).first()
        else:
            cart = None

        if not cart:
            raise NotFound("سبد خرید یافت نشد.")

        try:
            cart_item = CartItem.objects.select_related('quotation').get(
                id=cart_item_id,
                cart=cart,
            )
        except CartItem.DoesNotExist:
            raise NotFound("آیتم سبد خرید یافت نشد.")

        quotation = getattr(cart_item, 'quotation', None)
        if not quotation:
            raise NotFound("هیچ پیش‌فاکتوری برای این آیتم سبد خرید وجود ندارد.")

        return quotation