from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

from .managers import NotificationManager

# ====== Notification Model ====== #
class CustomerNotification(models.Model):
    """
    مدل اطلاع رسانی پویا.
    این مدل پیام‌های سیستم یا سایر کاربران را برای یک کاربر خاص ذخیره می‌کند.
    """
    recipient = models.ForeignKey(
        "core.User", 
        related_name='notifications', 
        on_delete=models.CASCADE,
        verbose_name=_("گیرنده")
    )
    # sender می‌تواند null باشد (یعنی پیام سیستمی است)
    sender = models.ForeignKey(
        "core.User", 
        related_name='sent_notifications', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        verbose_name=_("فرستنده")
    )
    name = models.CharField(_('عنوان'), max_length=150)
    message = models.TextField(_('متن پیام'), blank=True, null=True)
    
    # ===== وضعیت خوانده شدن ===== #
    is_read = models.BooleanField(_("خوانده شده"), default=False)
    
    # ===== اتصال پویا (Generic Relation) ===== #
    content_type = models.ForeignKey(ContentType, verbose_name=_("نوع مدل"), on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField(_("آی‌دی شیء"))
    content_object = GenericForeignKey('content_type', 'object_id')
    
    created_at = models.DateTimeField(_('تاریخ ایجاد'), auto_now_add=True)
    updated_at = models.DateTimeField(_('تاریخ به روزرسانی'), auto_now=True)
    
    objects = NotificationManager()
    
    def __str__(self):
        return f"{self.name} -> {self.recipient.phone_number}"
    
    class Meta:
        db_table = 'customer_notification'
        verbose_name = _('اعلان')
        verbose_name_plural = _('اعلان ها')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient', 'is_read']), # برای کوئری "تعداد پیام‌های ناخوانده"
        ]

    # ===== رفتارهای مدل (Domain Logic) ===== #
    def mark_as_read(self):
        """تغییر وضعیت به خوانده شده"""
        if not self.is_read:
            self.is_read = True
            self.save(update_fields=['is_read', 'updated_at'])

    def mark_as_unread(self):
        """تغییر وضعیت به خوانده نشده"""
        if self.is_read:
            self.is_read = False
            self.save(update_fields=['is_read', 'updated_at'])
