# from django.db import models
# from django.utils.translation import gettext_lazy as _
# from django.conf import settings
# from django.contrib.contenttypes.fields import GenericForeignKey
# from django.contrib.contenttypes.models import ContentType
# from core.models import Order

# # ===== Ticket Type Model ===== #
# class TicketType(models.Model):
#     """
#     نوع تیکت (مثلا: تاییدیه، اعلام نقص، سوال فنی).
#     این جدول به ادمین اجازه می‌دهد دسته‌بندی تیکت‌ها را مدیریت کند.
#     """
#     title = models.CharField(_("عنوان"), max_length=100)
#     code = models.SlugField(_("کد سیستمی"), unique=True, help_text="برای استفاده در شروط برنامه (غیر قابل تغییر)")
    
#     description = models.TextField(_("توضیحات"), blank=True)
#     is_active = models.BooleanField(default=True)
    
#     created_at = models.DateTimeField(auto_now_add=True)

#     class Meta:
#         verbose_name = _("نوع تیکت")
#         verbose_name_plural = _("انواع تیکت")

#     def __str__(self):
#         return self.title

# # ===== Ticket Status Model ===== #
# class TicketStatus(models.Model):
#     """
#     وضعیت‌های تیکت (مثلا: باز، در حال بررسی، بسته شده).
#     """
#     title = models.CharField(_("عنوان وضعیت"), max_length=100)
#     code = models.SlugField(_("کد سیستمی"), unique=True)
#     color = models.CharField(_("رنگ نمایش"), max_length=20, default="blue", help_text="نام رنگ یا کد hex")
#     # ===== آیا این وضعیت به معنی بسته شده هست؟ ===== #
#     is_closed_state = models.BooleanField(_("به معنی بسته شدن است؟"), default=False)
    
#     sort_order = models.PositiveIntegerField(default=0)

#     class Meta:
#         verbose_name = _("وضعیت تیکت")
#         verbose_name_plural = _("وضعیت‌های تیکت")
#         ordering = ['sort_order']

#     def __str__(self):
#         return self.title

# # ===== Internal Ticket Model ===== #
# class InternalTicket(models.Model):
#     """
#     سیستم تیکتینگ جامع با قابلیت اشاره به هر آبجکتی در سیستم.
#     (Order, OrderItem, CostItem, Transaction, ...)
#     """
#     PRIORITY_CHOICES = [
#         ('low', _('عادی')),
#         ('medium', _('مهم')),
#         ('high', _('فوری')),
#         ('critical', _('بحرانی')),
#     ]

#     # ===== مدل سفارش - چونکه نقطه ثقل این سیستم مدیریت داخلی، سفارشات است ===== #
#     order = models.ForeignKey(
#         Order, 
#         related_name='tickets', 
#         on_delete=models.CASCADE,
#         null=True, blank=True,
#         verbose_name=_("سفارش کلان")
#     )
    
#     # ===== فیلد مربوط به انتخاب مدل مربوطه ===== #
#     content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, verbose_name=_("نوع آیتم هدف"))
#     object_id = models.PositiveIntegerField(verbose_name=_("شناسه آیتم هدف"))
#     content_object = GenericForeignKey('content_type', 'object_id')

#     # ===== فرستنده و گیرنده ===== #
#     sender = models.ForeignKey(
#         settings.AUTH_USER_MODEL, 
#         related_name='created_tickets', 
#         on_delete=models.PROTECT,
#         verbose_name=_("ایجاد کننده")
#     )
    
#     # ===== نقش گیرنده ===== #
#     target_role = models.ForeignKey(
#         'core.Role', 
#         related_name='assigned_tickets', 
#         on_delete=models.PROTECT,
#         verbose_name=_("واحد مسئول")
#     )
    
#     # ===== کاربر گیرنده ===== #
#     target_user = models.ForeignKey(
#         settings.AUTH_USER_MODEL, 
#         related_name='personal_tickets', 
#         on_delete=models.SET_NULL, 
#         null=True, blank=True,
#         verbose_name=_("کاربر مسئول")
#     )
    
#     # --- محتوا --- #
#     title = models.CharField(_("عنوان"), max_length=200)
#     description = models.TextField(_("توضیحات"))
#     attachment = models.FileField(_("پیوست"), upload_to='tickets/%Y/%m/', blank=True, null=True)
    
#     priority = models.CharField(_("اولویت"), max_length=20, choices=PRIORITY_CHOICES, default='medium')
#     ticket_type = models.ForeignKey(
#         TicketType, 
#         on_delete=models.PROTECT, 
#         verbose_name=_("نوع تیکت")
#     )
    
#     status = models.ForeignKey(
#         TicketStatus, 
#         on_delete=models.PROTECT, 
#         verbose_name=_("وضعیت"),
#         related_name="tickets"
#     )
    
#     created_at = models.DateTimeField(auto_now_add=True)
#     closed_at = models.DateTimeField(null=True, blank=True)

#     class Meta:
#         verbose_name = _('تیکت داخلی')
#         verbose_name_plural = _('تیکت‌های داخلی')
#         ordering = ['-created_at']
#         indexes = [
#             models.Index(fields=["content_type", "object_id"]),
#         ]

#     def __str__(self):
#         return f"{self.title} -> {self.target_role}"

# # ===== Ticket Activity Logs ===== #
# class TicketActivityLog(models.Model):
#     """
#     جدول ردیابی کامل (Audit Log).
#     هر اتفاقی که روی تیکت بیفتد اینجا ثبت می‌شود.
#     """
#     ACTION_TYPES = [
#         ('created', _('ایجاد تیکت')),
#         ('status_change', _('تغییر وضعیت')),
#         ('assigned', _('تغییر مسئول')),
#         ('comment', _('ارسال پاسخ')),
#         ('priority_change', _('تغییر اولویت')),
#     ]

#     ticket = models.ForeignKey(InternalTicket, related_name='logs', on_delete=models.CASCADE)
#     actor = models.ForeignKey(
#         settings.AUTH_USER_MODEL, 
#         on_delete=models.PROTECT,
#         verbose_name=_("انجام دهنده")
#     )
    
#     action = models.CharField(_("نوع فعالیت"), max_length=20, choices=ACTION_TYPES)
#     # ===== وضعیت قبلی و وضعیت جدید تیکت ===== #
#     previous_value = models.CharField(max_length=255, blank=True, null=True)
#     new_value = models.CharField(max_length=255, blank=True, null=True)
    
#     description = models.TextField(_("توضیحات سیستم"), blank=True)
#     timestamp = models.DateTimeField(auto_now_add=True)

#     class Meta:
#         ordering = ['-timestamp']
#         verbose_name = _('لاگ فعالیت تیکت')

# # ===== Ticket Reply ===== #
# class TicketReply(models.Model):
#     """
#     مدل پاسخگویی به هر تیکت و ایونت
#     """
#     ticket = models.ForeignKey(InternalTicket, related_name='replies', on_delete=models.CASCADE)
#     user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
#     message = models.TextField(_("متن پاسخ"))
#     is_internal_note = models.BooleanField(default=False)
#     attachment = models.FileField(upload_to='tickets/replies/', blank=True, null=True)
#     created_at = models.DateTimeField(auto_now_add=True)
    
#     class Meta:
#         ordering = ['created_at']