from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from slugify import slugify as unicode_slugify
from django.contrib.auth import get_user_model

from .managers import (
    ArticleManager,
    ArticleCategoryManager,
    TutorialManager,
)

User = get_user_model()

# ========== ARTICLE STATUS ========== #
class ArticleStatus(models.TextChoices):
    DRAFT = 'draft', _('پیش‌نویس')
    PUBLISHED = 'published', _('منتشر شده')
    ARCHIVED = 'archived', _('بایگانی شده')

# ========== ARTICLE CATEGORY ========== #
class ArticleCategory(models.Model):
    name = models.CharField(_("نام دسته‌بندی"), max_length=150)
    slug = models.SlugField(_("اسلاگ"), unique=True, blank=True, null=True)
    is_active = models.BooleanField(_("وضعیت"), default=0)
    created_at = models.DateTimeField(_("تاریخ ایجاد"), auto_now_add=True)
    updated_at = models.DateTimeField(_("تاریخ بروزرسانی"), auto_now=True)
    
    class Meta:
        verbose_name = _("دسته‌بندی مقاله")
        verbose_name_plural = _("دسته‌بندی‌های مقالات")

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unicode_slugify(self.name)
        super().save(*args, **kwargs)

    objects = ArticleCategoryManager()

    def __str__(self):
        return self.name

# ========== ARTICLE MODEL ========== #
class Article(models.Model):
    """ مدل مقالات بلاگ """
    title = models.CharField(_("عنوان مقاله"), max_length=255)
    slug = models.SlugField(_("اسلاگ"), unique=True, blank=True, null=True, max_length=255)
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='articles', verbose_name=_("نویسنده"))
    category = models.ForeignKey(ArticleCategory, on_delete=models.PROTECT, related_name='articles', verbose_name=_("دسته‌بندی"))
    
    summary = models.TextField(_("خلاصه مقاله"), help_text=_("برای نمایش در لیست مقالات"))
    content = models.TextField(_("متن کامل"))
    image = models.ImageField(_("تصویر کاور"), upload_to='blog/covers/')
    
    # ===== سئو و متا دیتا =====
    meta_title = models.CharField(_("عنوان سئو (Meta Title)"), max_length=150, blank=True, null=True)
    meta_description = models.CharField(_("توضیحات سئو (Meta Description)"), max_length=255, blank=True, null=True)
    tags = models.CharField(_("تگ‌ها"), max_length=255, help_text=_("با کاما جدا کنید"), blank=True)
    
    # ===== آمار و وضعیت =====
    read_time = models.PositiveSmallIntegerField(_("زمان مطالعه (دقیقه)"), default=5)
    views_count = models.PositiveIntegerField(_("تعداد بازدید"), default=0)
    status = models.CharField(_("وضعیت"), max_length=15, choices=ArticleStatus.choices, default=ArticleStatus.DRAFT)
    
    # ===== روابط تجاری =====
    related_products = models.ManyToManyField("core.Product", blank=True, verbose_name=_("محصولات مرتبط"))
    
    # ===== تاریخ‌ها =====
    published_at = models.DateTimeField(_("تاریخ انتشار"), blank=True, null=True)
    created_at = models.DateTimeField(_("تاریخ ایجاد"), auto_now_add=True)
    updated_at = models.DateTimeField(_("تاریخ بروزرسانی"), auto_now=True)

    objects = ArticleManager()

    class Meta:
        verbose_name = _("مقاله")
        verbose_name_plural = _("مقالات")
        ordering = ['-published_at', '-created_at']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unicode_slugify(self.title)
        if self.status == ArticleStatus.PUBLISHED and not self.published_at:
            self.published_at = timezone.now()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

# ========== TUTORIAL ========== #
class Tutorial(models.Model):
    """ مدل آموزش‌های سایت (معمولا ویدیو محور برای راهنمایی کاربران) """
    title = models.CharField(_("عنوان آموزش"), max_length=255)
    slug = models.SlugField(_("اسلاگ"), unique=True, blank=True, null=True, max_length=255)
    description = models.TextField(_("توضیحات"), blank=True, null=True)
    
    # ===== مدیا و فایل ===== #
    youtube_embed_url = models.URLField(_("لینک Embed یوتیوب/آپارات"), help_text=_("لینک مستقیم iframe"))
    thumbnail = models.ImageField(_("تصویر کاور ویدیو"), upload_to='tutorials/thumbnails/', blank=True, null=True)
    attachment_file = models.FileField(_("فایل تمرین/قالب"), upload_to='tutorials/attachments/', blank=True, null=True, help_text=_("فایل لایه باز یا قالب برای دانلود کاربر"))

    is_active = models.BooleanField(_("فعال/نمایش داده شود؟"), default=True)
    
    # ===== روابط تجاری ===== #
    related_products = models.ManyToManyField("core.Product", blank=True, verbose_name=_("مربوط به کدام محصولات؟"))

    created_at = models.DateTimeField(_("تاریخ ایجاد"), auto_now_add=True)
    updated_at = models.DateTimeField(_("تاریخ بروزرسانی"), auto_now=True)

    objects = TutorialManager()

    class Meta:
        verbose_name = _("آموزش")
        verbose_name_plural = _("آموزش‌ها")
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unicode_slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
