import uuid
from slugify import slugify

from django.db import models
from django.contrib.auth.models import Permission
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin 
from django.utils.translation import gettext_lazy as _

from .managers import (
    UserManager, RoleManager,
    CustomerProfileManager,
    AddressManager, ProvinceManager,
    CityManager
)

# ====== User Model ====== #
class User(AbstractBaseUser, PermissionsMixin):
    """
    مدل کاربر با ایمیل و رمز عبور
    """
    id = models.AutoField(
        primary_key=True,
        db_column='id',
        verbose_name='شناسه',
        help_text='شناسه کاربری',
    )
    phone_number = models.CharField(_("شماره تماس"), max_length=15, unique=True)
    is_active = models.BooleanField(_('فعال'), default=True)
    is_staff = models.BooleanField(_('کاربری'), default=False)
    is_superuser = models.BooleanField(_('ادمین'), default=False)
    is_verified = models.BooleanField(_('تایید شده'), default=False)
    
    created_at = models.DateTimeField(_('تاریخ عضویت'), auto_now_add=True)
    updated_at = models.DateTimeField(_('تاریخ به روزرسانی'), auto_now=True)
    
    # قرار دادن شماره تماس به عنوان فیلد اصلی لاگین
    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = []
    
    objects = UserManager()
    
    def __str__(self):
        return f"{self.phone_number}"

# ========= Role Model ========= #
class Role(models.Model):
    """ مدلاسیون نقش کاربر """
    USER_TYPE = [
        ("admin", _("ادمین")),
        ("normal", _("کاربر عادی")),
    ]
    
    name = models.CharField(_('نام'), max_length=150)
    slug = models.SlugField(_('کد سیستمی'), unique=True, null=True, blank=True)
    description = models.TextField(_('توضیحات'), blank=True, null=True)
    permission = models.ManyToManyField(Permission, verbose_name=_('مجوز ها'), related_name='roles')

    allowed_groups = models.ManyToManyField(
        'OrderStatusGroup',
        verbose_name=_("گروه‌های وضعیت مجاز"),
        related_name='roles',
        blank=True
    )
    type = models.CharField(_('نوع کاربر'), max_length=150, choices=USER_TYPE, default='normal')
    is_customer = models.BooleanField(_("آیا نقش برای مشتری است؟"), default=False)
    created_at = models.DateTimeField(_('تاریخ ایجاد'), auto_now_add=True)
    updated_at = models.DateTimeField(_('تاریخ به روزرسانی'), auto_now=True)
    
    objects = RoleManager()
    
    @property
    def allowed_status_groups(self):
        """
        تبدیل ریلیشن به لیست رشته‌ها برای استفاده راحت در سرویس
        خروجی: ['design', 'qc']
        """
        return list(self.allowed_groups.values_list('code', flat=True))
    
    class Meta:
        app_label = 'core'
        verbose_name = _('نقش')
        verbose_name_plural = _('نقش ها')

    def __str__(self):
        return self.name


# ======== User Role Model ======== #
class UserRole(models.Model):
    """User Role Model"""
    user = models.ForeignKey(User, related_name='user_role', on_delete=models.CASCADE)
    role = models.ForeignKey(Role, related_name='role_user', on_delete=models.CASCADE)

    created_at = models.DateTimeField(_('تاریخ عضویت'), auto_now_add=True)
    updated_at = models.DateTimeField(_('تاریخ به روزرسانی'), auto_now=True)

    class Meta:
        app_label = 'core'
        verbose_name = _('واسط نقش کاربر')
        verbose_name_plural = _('واسط نقش های کاربر')
        
    def __str__(self):
        return f"{self.user.username} - {self.role.name}"

# ========= Customer Profile Model ========= #
class CustomerProfile(models.Model):
    """ مدل مربوط به پروفایل مشتری """
    user = models.OneToOneField("core.User", related_name='customer_profile', on_delete=models.CASCADE)
    first_name = models.CharField(_('نام'), max_length=150)
    last_name = models.CharField(_('نام خانوادگی'), max_length=150)
    # phone_number = models.CharField(_('شماره تماس'), max_length=150)
    company = models.CharField(_('نام شرکت'), max_length=150, blank=True, null=True)
    bio = models.TextField(_('بیوگرافی'), blank=True, null=True)
    created_at = models.DateTimeField(_('تاریخ ایجاد'), auto_now_add=True)
    updated_at = models.DateTimeField(_('تاریخ به روزرسانی'), auto_now=True)
    
    objects = CustomerProfileManager()
    
    def fullname(self):
        return self.first_name + " " + self.last_name
    
    def __str__(self):
        return self.first_name + " " + self.last_name
    
    class Meta:
        app_label = 'core'
        verbose_name = _('مشتری')
        verbose_name_plural = _('مشتریان')

# ===== Province Model ===== #
class Province(models.Model):
    """ مدل استان """
    name = models.CharField(_('نام'), max_length=150)
    slug = models.SlugField(_('نامک'), unique=True, null=True, blank=True)
    created_at = models.DateTimeField(_('تاریخ ایجاد'), auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    objects = ProvinceManager()
    
    class Meta:
        app_label = 'core'
        verbose_name = _('استان')
        verbose_name_plural = _('استان ها')
    
    def __str__(self):
        return f"{self.name}"
    
    def save(self, *args, **kwargs):
        """ ذخیره نام به صورت خودکار """
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)

# ===== City Model ===== #
class City(models.Model):
    """ مدل شهر """
    name = models.CharField(_('نام'), max_length=150)
    slug = models.SlugField(_('نامک'), unique=True, null=True, blank=True)
    province = models.ForeignKey(Province, related_name='cities', on_delete=models.CASCADE)
    created_at = models.DateTimeField(_('تاریخ ایجاد'), auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    objects = CityManager()

    class Meta:
        app_label = 'core'
        verbose_name = _('شهر')
        verbose_name_plural = _('شهر ها')

    def __str__(self):
        return f"{self.name}"

    def save(self, *args, **kwargs):
        """ ذخیره کد به صورت خودکار  """
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)

# ===== Address Model ===== #
class Address(models.Model):
    """ مدل آدرس """
    user = models.ForeignKey("core.User", related_name='addresses', on_delete=models.CASCADE)
    province = models.ForeignKey(Province, verbose_name=_("استان"), on_delete=models.CASCADE)
    city = models.ForeignKey(City, verbose_name=_("شهر"), on_delete=models.CASCADE)
    postal_code = models.CharField(
        _('کد پستی'), 
        max_length=10, 
        null=True, 
        blank=True
    )
    address = models.TextField(_('آدرس'))
    created_at = models.DateTimeField(_('تاریخ ایجاد'), auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    objects = AddressManager()

    class Meta:
        app_label = 'core'
        verbose_name = _('آدرس')
        verbose_name_plural = _('آدرس ها')
