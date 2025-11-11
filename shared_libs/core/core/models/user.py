from django.db import models
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
