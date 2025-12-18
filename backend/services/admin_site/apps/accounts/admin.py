from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from core.site import custom_admin_site
from core.models import(
    User,
    UserRole,
    Role,
    Wallet,
    WalletTransaction,
    Address,
    City,
    Province,
    CustomerProfile,
    OrderItem,
    Order,
    OrderStatus,
    OrderStatusGroup,
    OrderItemFile
)
# ========================================== #
# ========== User Role Inline ============== #
# ========================================== #
class UserRoleInline(admin.TabularInline):
    """
    این کلاس باعث می‌شود وقتی وارد صفحه ویرایش کاربر می‌شوی،
    بتوانی همانجا نقش او را هم تعیین کنی.
    """
    model = UserRole
    extra = 0 # فیلد خالی اضافه نشان نده
    autocomplete_fields = ['role'] # برای لیست‌های طولانی نقش عالی است

# ========================================== #
# ========== User Admin Config ============= #
# ========================================== #
@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    تنظیمات نمایش کاربران در پنل ادمین.
    """
    # ستون‌هایی که در لیست کاربران نمایش داده می‌شوند
    list_display = ('username', 'email', 'get_role_name', 'is_staff', 'is_active', 'created_at')
    
    # فیلترهای سایدبار (سمت راست)
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'user_role__role')
    
    # فیلدهای قابل جستجو
    search_fields = ('username', 'email', 'phone_number')
    
    # ترتیب نمایش
    ordering = ('-created_at',)
    
    # اضافه کردن بخش نقش‌ها به فرم ویرایش کاربر
    inlines = [UserRoleInline]

    # شخصی‌سازی فیلدها در صفحه ویرایش (Fieldsets)
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('اطلاعات شخصی'), {'fields': ('email',)}), # اگر فرست نیم و لست نیم در پروفایل است، اینجا نگذار
        (_('دسترسی‌ها'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('تاریخ‌های مهم'), {'fields': ('last_login', 'created_at')}),
    )
    
    readonly_fields = ('created_at', 'last_login')

    # متد کمکی برای نمایش نام نقش در لیست کاربران
    def get_role_name(self, obj):
        role_rel = obj.user_role.first()
        if role_rel:
            return role_rel.role.name
        return "-"
    get_role_name.short_description = _('نقش سازمانی')

# ========================================== #
# ========== Role Admin Config ============= #
# ========================================== #
@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    """
    مدیریت نقش‌ها.
    """
    list_display = ('name', 'slug', 'get_allowed_groups_count')
    search_fields = ('name', 'slug')

    filter_horizontal = ('allowed_groups',) 

    def get_allowed_groups_count(self, obj):
        return obj.allowed_groups.count()
    get_allowed_groups_count.short_description = _('تعداد اسکوپ‌ها')

custom_admin_site.register(User)
custom_admin_site.register(UserRole)
custom_admin_site.register(Wallet)
custom_admin_site.register(WalletTransaction)
custom_admin_site.register(Address)
custom_admin_site.register(City)
custom_admin_site.register(Province)
custom_admin_site.register(CustomerProfile)
custom_admin_site.register(OrderItem)
custom_admin_site.register(Order)
custom_admin_site.register(OrderStatus)
custom_admin_site.register(OrderStatusGroup)
custom_admin_site.register(OrderItemFile)
