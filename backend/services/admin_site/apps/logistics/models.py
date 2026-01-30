from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

from .managers import (
    PackageManager,
    ShipmentManager,
)

# ===== Order Shipment ===== #
class OrderShipment(models.Model):
    """
    مدل مرسوله.
    این مدل مشخص می‌کند "چه زمانی" و "چگونه" بار ارسال می‌شود.
    یک سفارش ممکن است در ۲ مرسوله جداگانه ارسال شود (Split Shipment).
    """
    SHIPMENT_STATUS = [
        ('processing', _('در حال پردازش انبار')),
        ('ready_to_ship', _('آماده ارسال')),
        ('dispatched', _('تحویل به متصدی')),
        ('delivered', _('تحویل مشتری شد')),
        ('returned', _('مرجوع شد')),
    ]
    
    METHOD_CHOICES = [
        ('terminal', _('باربری ترمینال')),
        ('pickup', _('تحویل حضوری(درب کارگاه)')),
        ('other', _('سایر')),
    ]
    
    order = models.ForeignKey(
        'core.Order', 
        related_name='shipments', 
        on_delete=models.CASCADE,
        verbose_name=_("سفارش مربوطه")
    )
    
    delivery_method = models.CharField(
        _("روش ارسال"), 
        max_length=50, 
        choices=METHOD_CHOICES,
        default='other'
    )

    # ===== اطلاعات ارسال ===== #
    destination_address = models.TextField(_("آدرس مورد نظر"), blank=True, null=True)
    
    # ===== اطلاعات تحویل ===== #
    tracking_code = models.CharField(_("کد رهگیری پستی"), max_length=100, blank=True, null=True)
    driver_info = models.TextField(_("اطلاعات راننده/پیک"), blank=True, help_text="نام و شماره تماس پیک")
    
    shipping_cost_real = models.DecimalField(_("هزینه واقعی ارسال"), max_digits=15, decimal_places=0, default=0, help_text="هزینه‌ای که ما به پست پرداختیم")
    
    status = models.CharField(_("وضعیت مرسوله"), max_length=20, choices=SHIPMENT_STATUS, default='processing')
    
    # ===== زمان های تحویل ===== #
    expected_delivery_date = models.DateTimeField(_("زمان احتمالی تحویل"), null=True, blank=True)
    dispatched_at = models.DateTimeField(_("زمان خروج از انبار"), null=True, blank=True)
    delivered_at = models.DateTimeField(_("زمان تحویل به مشتری"), null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    objects = ShipmentManager()

    class Meta:
        db_table = 'admin_order_shipments'
        verbose_name = _('مرسوله پستی')
        verbose_name_plural = _('مرسولات پستی')
        
    def __str__(self):
        return f"Shipment #{self.id} | {self.get_status_display()}"

# =====  Order Package Model  ===== #
class OrderPackage(models.Model):
    """
    مدل بسته‌بندی فیزیکی (کارتن/پاکت).
    این مدل دقیقاً همان "لیبل" است.
    اگر یک مرسوله شامل ۳ کارتن باشد، ۳ رکورد در این جدول داریم.
    """
    shipment = models.ForeignKey(
        OrderShipment, 
        related_name='packages', 
        on_delete=models.CASCADE,
        verbose_name=_("مرسوله")
    )
    
    # ===== اطلاعات مربوط به لیبل ===== #
    label_uuid = models.CharField(_("شناسه لیبل"), max_length=50, editable=False, unique=True, null=True, blank=True)
    # ===== محتویات داخل بسته ===== #
    customer_name = models.CharField(_("نام مشتری"), max_length=150, null=True, blank=True)
    phone_number = models.CharField(_("شماره تماس"), max_length=11, null=True, blank=True)
    address = models.TextField(_("آدرس"), null=True, blank=True)
    order_image = models.ImageField(_("تصویر سفارش"), null=True, blank=True)
    content_summary = models.TextField(_("خلاصه محتویات"), blank=True, help_text="مثلا: ۱۰۰۰ عدد کارت ویزیت لمینت")
    # ===== مسئول بسته بندی ===== #
    packed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.PROTECT, 
        null=True, 
        verbose_name=_("انباردار")
    )
    # ===== تاریخ بسته بندی ===== #
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    objects = PackageManager()

    class Meta:
        db_table = 'admin_order_packages'
        verbose_name = _('بسته/کارتن')
        verbose_name_plural = _('بسته‌ها و لیبل‌ها')

    def __str__(self):
        return f"{self.customer_name} - {self.label_code}"
    
    @property
    def label_code(self):
        """کد کوتاه خوانا برای چاپ روی لیبل"""
        return str(self.label_uuid).split('-')[0].upper()