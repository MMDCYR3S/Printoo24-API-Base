from rest_framework import serializers
from django.utils.translation import gettext_lazy as _

# ===== Customer Profile Serializer ===== #
class CustomerProfileSerializer(serializers.Serializer):
    """
    سریالایزر یکپارچه برای دریافت و ویرایش اطلاعات
    """
    
    # ===== فیلد های مدل کاربر ===== #
    username = serializers.CharField(read_only=True)
    email = serializers.EmailField(read_only=True, label=_("آدرس ایمیل"))

    # ===== فیلد های مدل پروفایل ===== #
    first_name = serializers.CharField(required=False, max_length=150, label=_('نام'))
    last_name = serializers.CharField(required=False, max_length=150, label=_('نام خانوادگی'))
    phone_number = serializers.CharField(required=False, max_length=11, label=_('شماره تماس'))
    company = serializers.CharField(required=False, allow_blank=True, max_length=150, label=_('نام شرکت'))
    bio = serializers.CharField(required=False, allow_blank=True, label=_('بیوگرافی'))
    
    # ===== سایر اطلاعات ===== #
    is_active = serializers.BooleanField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    