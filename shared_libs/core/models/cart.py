from django.db import models
from django.utils.translation import gettext_lazy as _

from .product import Product, ProductFileUploadRequirement

# ===== Cart Model ===== #
class Cart(models.Model):
    """ مدل سبد خرید """
    user = models.ForeignKey("core.User", verbose_name=_("کاربر"), on_delete=models.CASCADE)
    created_at = models.DateTimeField(_('تاریخ ایجاد'), auto_now_add=True)
    updated_at = models.DateTimeField(_('تاریخ به روزرسانی'), auto_now=True)
    
    def __str__(self):
        return f"{self.user.username}"
    
    class Meta:
        verbose_name = _('سبد خرید')
        verbose_name_plural = _('سبدهای خرید')
        
# ====== Cart Item Model ====== #
class CartItem(models.Model):
    """ مدل آیتم سبد خرید """
    cart = models.ForeignKey(Cart, related_name='cart_items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name='cart_items', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(_('تعداد'), default=1)
    price = models.DecimalField(_('قیمت'), max_digits=12, decimal_places=2)
    items = models.JSONField(_('آیتم های اضافی'), blank=True, null=True)
    created_at = models.DateTimeField(_('تاریخ ایجاد'), auto_now_add=True)
    updated_at = models.DateTimeField(_('تاریخ به روزرسانی'), auto_now=True)

    def __str__(self):
        return f"{self.cart.user.username} - {self.product.name}"
    
    class Meta:
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
    requirement = models.ForeignKey(
        ProductFileUploadRequirement,
        verbose_name=_("نیازمندی مربوطه"),
        on_delete=models.PROTECT 
    )
    file = models.FileField(_("فایل"), upload_to='cart_uploads/%Y/%m/%d/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"File for {self.cart_item}"

    class Meta:
        verbose_name = _("فایل آپلود شده سبد خرید")
        verbose_name_plural = _("فایل‌های آپلود شده سبد خرید")
