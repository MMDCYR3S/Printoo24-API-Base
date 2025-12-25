from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

from .managers import AuditLogManager

# ==========  LOG MODEL ========== #
class AuditLog(models.Model):
    """
    سیستم مرکزی ثبت وقایع (Audit Trail).
    قابلیت اتصال به تمام مدل‌های سیستم (مالی، انبار، کاربران، سفارشات).
    """
    ACTION_CHOICES = [
        ('CREATE', _('ایجاد')),
        ('UPDATE', _('ویرایش')),
        ('DELETE', _('حذف')),
        ('LOGIN', _('ورود به سیستم')),
        ('LOGOUT', _('خروج')),
        ('approve', _('تایید کردن')),
        ('reject', _('رد کردن')),
        ('change_pass', _('تغییر رمز عبور')),
        ('assignment', _('تخصیص وظیفه')),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        verbose_name=_("کاربر"),
        related_name='audit_logs'
    )
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')

    action = models.CharField(_("نوع عملیات"), max_length=20, choices=ACTION_CHOICES, db_index=True)

    changes = models.JSONField(_("تغییرات داده‌ای"), default=dict, blank=True)
    
    description = models.TextField(_("توضیحات سیستمی/دستی"), blank=True)

    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=255, blank=True, null=True, help_text="Browser Info")
    
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    
    objects = AuditLogManager()

    class Meta:
        db_table = 'admin_audit_logs'
        verbose_name = _('لاگ سیستم')
        verbose_name_plural = _('لاگ‌های سیستم')
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['content_type', 'object_id']), 
        ]

    def __str__(self):
        return f"Log: {self.user} -> {self.action} -> {self.content_type}"
