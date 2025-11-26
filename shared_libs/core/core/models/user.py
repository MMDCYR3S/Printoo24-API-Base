from slugify import slugify

from django.db import models
from django.contrib.auth.models import Permission
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin 
from django.utils.translation import gettext_lazy as _

# ====== User Manager ====== #
class UserManager(BaseUserManager):
    """ 
    مدیر سفارشی برای مدل User که با ایمیل به عنوان شناسه یکتا کار می‌کند.
    """

    def create_user(self, username, email, password=None, **extra_fields):
        """
        یک کاربر جدید ایجاد و ذخیره می‌کند.
        """
        if not email:
            raise ValueError(_('The Email must be set'))
        if not username:
            raise ValueError(_('The Username must be set'))
            
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        """
        یک ابرکاربر (superuser) جدید ایجاد و ذخیره می‌کند.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_verified', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))
            
        return self.create_user(username, email, password, **extra_fields)

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
    username = models.CharField(_("نام کاربری"), max_length=150, unique=True)
    email = models.EmailField(_('آدرس ایمیل'), unique=True)
    is_active = models.BooleanField(_('فعال'), default=True)
    is_staff = models.BooleanField(_('کاربری'), default=False)
    is_superuser = models.BooleanField(_('ادمین'), default=False)
    is_verified = models.BooleanField(_('تایید شده'), default=False)
    
    created_at = models.DateTimeField(_('تاریخ عضویت'), auto_now_add=True)
    updated_at = models.DateTimeField(_('تاریخ به روزرسانی'), auto_now=True)
    
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']
    
    objects = UserManager()
    
    def __str__(self):
        return f"{self.username}"
    
    class Meta:
        verbose_name = _('کاربر')
        verbose_name_plural = _('کاربران')

# ========= Role Model ========= #
class Role(models.Model):
    """ مدلاسیون نقش کاربر """
    name = models.CharField(_('نام'), max_length=150)
    description = models.TextField(_('توضیحات'), blank=True, null=True)
    permission = models.ManyToManyField(Permission, verbose_name=_('مجوز ها'), related_name='roles')
    created_at = models.DateTimeField(_('تاریخ ایجاد'), auto_now_add=True)
    updated_at = models.DateTimeField(_('تاریخ به روزرسانی'), auto_now=True)
    
    class Meta:
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
        verbose_name = _('نقش کاربر')
        verbose_name_plural = _('نقش های کاربر')
        
    def __str__(self):
        return f"{self.user.username} - {self.role.name}"

# ====== Wallet Model ====== #
class Wallet(models.Model):
    """ مدل کیف پول """
    user = models.OneToOneField("core.User", verbose_name=_("کاربر"), on_delete=models.CASCADE)
    decimal = models.DecimalField(_("مقدار"), max_digits=12, decimal_places=2, default=0)
    created_at = models.DateTimeField(_('تاریخ ایجاد'), auto_now_add=True)
    updated_at = models.DateTimeField(_('تاریخ به روزرسانی'), auto_now=True)
    
    def __str__(self):
        return self.user.username
    
# ====== Wallet Transaction Model ====== #
class WalletTransaction(models.Model):
    """
    مدل تراکنش های کیف پول
    """
    TRANSACTION_TYPE = [
        ("1", _("افزایش")),
        ("2", _("کاهش")),
        ("3", _("تایید")),
        ("4", _("رد")),
        ("5", _("برگشت")),
        ("6", _("پرداخت")),
        ("7", _("دریافت")),
        ("8", _("تایید پرداخت")),
        ("9", _("رد پرداخت")),
    ]
    
    user = models.ForeignKey("core.User", related_name="wallet_transactions", on_delete=models.CASCADE)
    type = models.CharField(_("نوع"), max_length=150, choices=TRANSACTION_TYPE)
    amount = models.DecimalField(_("مقدار"), max_digits=12, decimal_places=2, default=0)
    amount_after = models.DecimalField(_("مقدار بعد از عملیات"), max_digits=12, decimal_places=2, default=0)
    created_at = models.DateTimeField(_('تاریخ ایجاد'), auto_now_add=True)
    updated_at = models.DateTimeField(_('تاریخ به روزرسانی'), auto_now=True)

# ========= Customer Profile Model ========= #
class CustomerProfile(models.Model):
    """ مدل مربوط به پروفایل مشتری """
    user = models.OneToOneField("core.User", related_name='customer_profile', on_delete=models.CASCADE)
    first_name = models.CharField(_('نام'), max_length=150)
    last_name = models.CharField(_('نام خانوادگی'), max_length=150)
    phone_number = models.CharField(_('شماره تماس'), max_length=150)
    company = models.CharField(_('نام شرکت'), max_length=150, blank=True, null=True)
    bio = models.TextField(_('بیوگرافی'), blank=True, null=True)
    created_at = models.DateTimeField(_('تاریخ ایجاد'), auto_now_add=True)
    updated_at = models.DateTimeField(_('تاریخ به روزرسانی'), auto_now=True)
    
    def __str__(self):
        return self.first_name + " " + self.last_name
    
    class Meta:
        verbose_name = _('مشتری')
        verbose_name_plural = _('مشتریان')

# ===== Province Model ===== #
class Province(models.Model):
    """ مدل استان """
    name = models.CharField(_('نام'), max_length=150)
    slug = models.SlugField(_('نامک'), unique=True, null=True, blank=True)
    created_at = models.DateTimeField(_('تاریخ ایجاد'), auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
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
    postal_code = models.CharField(_('کد پستی'), max_length=10)
    address = models.TextField(_('آدرس'))
    created_at = models.DateTimeField(_('تاریخ ایجاد'), auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

