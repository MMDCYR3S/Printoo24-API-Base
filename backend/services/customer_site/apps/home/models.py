import os

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError

from .managers import (
    ContactUsManager, 
    ModalManager, 
    SliderManager,
    SiteMediaManager,
)

# ===== Contact Us ===== #
class ContactUs(models.Model):
    """
    این مدل برای ذخیره‌سازی پیام‌های تماس با ما که از سمت کاربران
    ارسال می‌شود طراحی شده است.
    """
    full_name = models.CharField(
        max_length=255, 
        verbose_name=_("نام و نام خانوادگی")
    )
    email = models.EmailField(
        verbose_name=_("ایمیل"),
        null=True,
        blank=True
    )
    phone_number = models.CharField(
        max_length=20, 
        verbose_name=_("شماره تماس")
    )
    subject = models.CharField(
        max_length=255, 
        verbose_name=_("موضوع پیام")
    )
    message = models.TextField(
        verbose_name=_("متن پیام")
    )
    is_read = models.BooleanField(
        default=False, 
        verbose_name=_("خوانده شده توسط ادمین")
    )
    admin_reply = models.TextField(_("پاسخ ادمین"), blank=True, null=True)
    replied_at = models.DateTimeField(_("تاریخ پاسخ"), blank=True, null=True)
    replied_by = models.ForeignKey(
        'core.User',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        verbose_name=_("پاسخ دهنده")
    )
    created_at = models.DateTimeField(
        auto_now_add=True, 
        verbose_name=_("تاریخ ایجاد")
    )
    
    objects = ContactUsManager()

    class Meta:
        db_table = 'customer_contact_us'
        verbose_name = _("پیام تماس با ما")
        verbose_name_plural = _("پیام‌های تماس با ما")
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.full_name} - {self.subject}"

    @property
    def is_replied(self):
        """ پراپرتی کمکی برای چک کردن وضعیت پاسخ """
        return bool(self.admin_reply)


# ===== Promotional Modal ===== #
class PromotionalModal(models.Model):
    """
    این مدل برای مدیریت مودال تبلیغاتی که در بدو ورود به سایت
    نمایش داده می‌شود، استفاده می‌گردد.
    نکته تحلیل‌گر: فیلد is_active برای کنترل نمایش مودال ضروری است.
    ما فقط باید اجازه دهیم یک مودال فعال باشد (این لاجیک باید در فرم ادمین یا سرویس چک شود).
    """
    title = models.CharField(
        max_length=255, 
        verbose_name=_("عنوان مودال")
    )
    description = models.TextField(
        verbose_name=_("توضیحات"),
        null=True,
        blank=True
    )
    # ===== برای تصاویر بهتر است از دایرکتوری مشخص استفاده شود ===== #
    image = models.ImageField(
        upload_to='banners/modals/', 
        verbose_name=_("تصویر مودال")
    )
    cta_text = models.CharField(
        max_length=100, 
        verbose_name=_("متن دکمه (CTA)")
    )
    cta_url = models.URLField(
        verbose_name=_("لینک دکمه")
    )
    is_active = models.BooleanField(
        default=False, 
        verbose_name=_("فعال")
    )
    created_at = models.DateTimeField(
        auto_now_add=True
    )
    
    objects = ModalManager()

    class Meta:
        db_table = 'customer_promotional_modal'
        verbose_name = _("مودال تبلیغاتی")
        verbose_name_plural = _("مودال‌های تبلیغاتی")

    def __str__(self):
        return f"{self.title} ({'فعال' if self.is_active else 'غیرفعال'})"

    # ===== متد کمکی برای دریافت تصویر ===== #
    @property
    def image_url(self):
        if self.image:
            return self.image.url
        return None

# ===== Slider Index ===== #
class SliderIndex(models.Model):
    """
    مدل مربوط به اسلادیر صفحه اصلی
    """
    name = models.CharField(_("نام"), max_length=255, blank=True, null=True)
    image = models.ImageField(_("تصویر"), upload_to='slider/')
    link = models.CharField(_("لینک مربوطه"), blank=True, null=True, max_length=500)
    created_at = models.DateTimeField(_("تاریخ ایجاد"), auto_now_add=True)
    updated_at = models.DateTimeField(_("تاریخ به روزرسانی"), auto_now=True)
    
    objects = SliderManager()
    
    def __str__(self):
        return self.name
    
    class Meta:
        db_table = 'customer_slider_index'
        verbose_name = _("اسلایدر")
        verbose_name_plural = _("اسلایدرها")
        ordering = ['-created_at']

# ========== Site Media ========== #
def validate_file_size_5mb(file):
    max_size_kb = 5120 # 5 MB
    if file.size > max_size_kb * 1024:
        raise ValidationError(_("حجم فایل نمی‌تواند بیشتر از ۵ مگابایت باشد."))

def validate_image_and_gif_extension(file):
    ext = os.path.splitext(file.name)[1].lower()
    valid_extensions = ['.jpg', '.jpeg', '.png', '.gif']
    if ext not in valid_extensions:
        raise ValidationError(_("فقط فایل‌های عکس (jpg, png) و گیف (gif) مجاز هستند."))

class SiteMedia(models.Model):
    """
    مدل ذخیره‌سازی فایل‌های تصویری و گیف
    """
    file = models.FileField(
        _("فایل رسانه"), 
        upload_to='site_media/',
        validators=[validate_file_size_5mb, validate_image_and_gif_extension]
    )
    link = models.CharField(_("لینک"), max_length=500, blank=True, null=True)
    is_active = models.BooleanField(_("وضعیت نمایش"), default=False)
    created_at = models.DateTimeField(_("تاریخ ایجاد"), auto_now_add=True)
    updated_at = models.DateTimeField(_("تاریخ به روزرسانی"), auto_now=True)
    
    objects = SiteMediaManager()
    
    class Meta:
        db_table = 'customer_site_media'
        verbose_name = _("رسانه سایت")
        verbose_name_plural = _("رسانه‌های سایت")
        ordering = ['-created_at']

    def __str__(self):
        return f"Media {self.id} - {self.file.name}"
