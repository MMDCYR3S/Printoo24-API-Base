from django.db import models
from django.utils.translation import gettext_lazy as _

from .product import Product, ProductFileUploadRequirement

# ===== Order Status Model ===== #
class OrderStatus(models.Model):
    """ مدل جداگانه برای وضعیت های سفارش """
    name = models.CharField(_('نام'), max_length=150)
    description = models.TextField(_('توضیحات'), blank=True, null=True)
    created_at = models.DateTimeField(_('تاریخ ایجاد'), auto_now_add=True)
    updated_at = models.DateTimeField(_('تاریخ به روزرسانی'), auto_now=True)

# ===== Order Model ===== #
class Order(models.Model):
    """ مدل سفارش  - این مدل، نقطه ثقل سیستم هستش. """
    ORDER_TYPE = [
        ("1", _("سفارش معمولی")),
        ("2", _("سفارش اختصاصی"))
    ]
    
    user = models.ForeignKey(
        "core.User",
        verbose_name=_("مشتری"),
        on_delete=models.PROTECT
    )
    type = models.CharField(_("نوع سفارش"), max_length=150, choices=ORDER_TYPE, default="2")
    order_status = models.ForeignKey(
        OrderStatus,
        verbose_name=_("وضعیت سفارش"),
        on_delete=models.PROTECT,
        related_name="order_status_order"
    )
    address = models.ForeignKey(
        "core.Address",
        verbose_name=_("آدرس"),
        on_delete=models.PROTECT,
        related_name="address_order",
        blank=True,
        null=True
    )
    total_price = models.DecimalField(_("قیمت کل"), max_digits=12, decimal_places=2)
    created_at = models.DateTimeField(_('تاریخ ایجاد'), auto_now_add=True)
    updated_at = models.DateTimeField(_('تاریخ به روزرسانی'), auto_now=True)
    
# ===== Order Item Model ===== #
class OrderItem(models.Model):
    """ مدل آیتم های سفارش """
    order = models.ForeignKey(Order, related_name='order_item_order', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name='order_item_product', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(_('تعداد'), default=1)
    price = models.DecimalField(_("قیمت"), max_digits=12, decimal_places=2)
    items = models.JSONField(_("آیتم های اضافی"), blank=True, null=True)
    created_at = models.DateTimeField(_('تاریخ ایجاد'), auto_now_add=True)
    updated_at = models.DateTimeField(_('تاریخ به روزرسانی'), auto_now=True)
    
    def __str__(self):
        return f"{self.order.pk} - {self.product.name}"

# ===== Order Item File Model ===== #
class OrderItemFile(models.Model):
    """ 
    فایل‌های نهایی طراحی برای آیتم سفارش.
    این مدل جایگزین DesignFile و OrderItemDesignFile می‌شود.
    """
    order_item = models.ForeignKey(
        OrderItem, 
        related_name='files', 
        on_delete=models.CASCADE,
        verbose_name=_("آیتم سفارش")
    )
    requirement = models.ForeignKey(
        ProductFileUploadRequirement, 
        on_delete=models.PROTECT,
        verbose_name=_("نوع فایل")
    )
    file = models.FileField(_('فایل نهایی'), upload_to='orders/designs/%Y/%m/%d/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('فایل آیتم سفارش')
        verbose_name_plural = _('فایل‌های آیتم سفارش')