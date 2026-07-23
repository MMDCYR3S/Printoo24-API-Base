from django.db import models
from django.utils.translation import gettext_lazy as _

from core.product.models import Product
from .managers import CartManager, CartItemManager

# ===== Cart Model ===== #
class Cart(models.Model):
    """ مدل سبد خرید """
    user = models.ForeignKey(
        "core.User", 
        verbose_name=_("کاربر"), 
        on_delete=models.CASCADE,
        null=True, blank=True
    )
    
    # ===== بخش ثبت اطلاعات کاربر ===== #
    session_key = models.CharField(
        _("شناسه نشست"), 
        max_length=40, 
        null=True, blank=True, 
        db_index=True,
        help_text="شناسه یکتا برای کاربران مهمان (معمولاً Session ID جنگو یا UUID)"
    )
    created_at = models.DateTimeField(_('تاریخ ایجاد'), auto_now_add=True)
    updated_at = models.DateTimeField(_('تاریخ به روزرسانی'), auto_now=True)
    
    objects = CartManager()
    
    def __str__(self):
        return f"{self.user.phone_number if self.user else self.session_key}"
    
    class Meta:
        db_table = 'customer_carts'
        verbose_name = _('سبد خرید')
        verbose_name_plural = _('سبدهای خرید')
        constraints = [
            models.CheckConstraint(
                check=models.Q(user__isnull=False) | models.Q(session_key__isnull=False),
                name='cart_user_or_session_required'
            )
        ]
        
# ====== Cart Item Model ====== #
class CartItem(models.Model):
    """ مدل آیتم سبد خرید """
    cart = models.ForeignKey(Cart, related_name='cart_items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name='cart_items', on_delete=models.CASCADE)
    name = models.CharField(_('نام'), max_length=255, blank=True, null=True)
    quantity = models.PositiveIntegerField(_('تعداد'), default=1)
    price = models.DecimalField(_('قیمت'), max_digits=14, decimal_places=2)
    items = models.JSONField(_('جزئیات سفارش'), blank=True, null=True)
    description = models.TextField(_('توضیحات'), blank=True, null=True)
    created_at = models.DateTimeField(_('تاریخ ایجاد'), auto_now_add=True)
    updated_at = models.DateTimeField(_('تاریخ به روزرسانی'), auto_now=True)
    
    objects = CartItemManager()

    def __str__(self):
        return f"{self.product.name} (x{self.quantity})"
    
    class Meta:
        db_table = 'customer_cart_items'
        verbose_name = _('آیتم سبد خرید')
        verbose_name_plural = _('آیتم های سبد خرید')

# ======== Cart Item Upload Model ======== #
class CartItemUpload(models.Model):
    """
    ذخیره فایل آپلود شده توسط کاربر برای یک آیتم خاص در سبد خرید.
    """
    cart_item = models.ForeignKey(
        CartItem,
        verbose_name=_("آیتم سبد خرید"),
        on_delete=models.CASCADE,
        related_name="uploads"
    )
    file = models.FileField(_("فایل"), upload_to='cart_uploads/%Y/%m/%d/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"File for {self.cart_item}"

    class Meta:
        db_table = 'customer_cart_item_uploads'
        verbose_name = _("فایل آپلود شده سبد خرید")
        verbose_name_plural = _("فایل‌های آپلود شده سبد خرید")
