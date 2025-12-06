from django.db import models
from django.utils.translation import gettext_lazy as _

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
    created_at = models.DateTimeField(
        auto_now_add=True, 
        verbose_name=_("تاریخ ایجاد")
    )

    class Meta:
        verbose_name = _("پیام تماس با ما")
        verbose_name_plural = _("پیام‌های تماس با ما")
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.full_name} - {self.subject}"


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

    class Meta:
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
    created_at = models.DateTimeField(_("تاریخ ایجاد"), auto_now_add=True)
    updated_at = models.DateTimeField(_("تاریخ به روزرسانی"), auto_now=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = _("اسلایدر")
        verbose_name_plural = _("اسلایدرها")
        ordering = ['-created_at']
    