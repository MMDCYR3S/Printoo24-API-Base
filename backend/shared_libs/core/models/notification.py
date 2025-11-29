from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

# ====== Notification Model ====== #
class CustomerNotification(models.Model):
    """
    مدل اطلاع رسانی
    این مدل به صورت کاملا پویا و حرفه ای به هر مدلی که نیاز بود، توانایی اتصال
    داره. این مدل به واسطه یک content type و یک content id، اطلاعاتی که میخواهیم
    به کاربر ارسال کنیم را با یک شیء دیگر (مثلا یک سفارش) متصل کنیم.
    """
    recipient = models.ForeignKey("core.User", related_name='notification_recipient', on_delete=models.CASCADE)
    sender = models.ForeignKey("core.User", related_name='notification_sender', on_delete=models.CASCADE)
    name = models.CharField(_('نام'), max_length=150)
    message = models.TextField(_('پیام'), blank=True, null=True)
    content_type = models.ForeignKey(ContentType, verbose_name=_("مدل مورد نظر"), on_delete=models.CASCADE)
    generic_key = GenericForeignKey('content_type', 'object_id')
    object_id = models.PositiveIntegerField(_("آی دی مورد نظر"))
    created_at = models.DateTimeField(_('تاریخ ایجاد'), auto_now_add=True)
    updated_at = models.DateTimeField(_('تاریخ به روزرسانی'), auto_now=True)
    
    def __str__(self):
        return f"{self.recipient.username}"
    
    class Meta:
        verbose_name = _('اعلان')
        verbose_name_plural = _('اعلان ها')
        
    