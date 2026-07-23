from rest_framework import serializers
from typing import List, Optional


# ===== Export Request Serializer ===== #
class ProductExportSerializer(serializers.Serializer):
    """
    سریالایزر برای درخواست استخراج محصولات
    """
    product_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        allow_empty=True,
        allow_null=True,
        help_text="لیست ID محصولات برای استخراج (اگر خالی باشد، همه محصولات استخراج می‌شوند)"
    )
    
    include_fields = serializers.BooleanField(
        default=True,
        help_text="آیا فیلدهای داینامیک محصولات در فایل Excel قرار گیرند؟"
    )
    
    include_formulas = serializers.BooleanField(
        default=True,
        help_text="آیا فرمول‌های قیمت‌گذاری در فایل Excel قرار گیرند؟"
    )


# ===== Import Request Serializer ===== #
class ProductImportSerializer(serializers.Serializer):
    """
    سریالایزر برای درخواست ایمپورت محصولات
    """
    file = serializers.FileField(
        help_text="فایل Excel حاوی محصولات (فرمت .xlsx)"
    )
    
    update_existing = serializers.BooleanField(
        default=False,
        help_text="آیا محصولات تکراری به‌روزرسانی شوند؟ (بر اساس نام محصول)"
    )
    
    skip_errors = serializers.BooleanField(
        default=True,
        help_text="آیا در صورت خطا در برخی سطرها، ادامه دهیم؟"
    )


# ===== Export/Import Response Serializers ===== #
class ExportResponseSerializer(serializers.Serializer):
    """
    سریالایزر پاسخ استخراج موفق
    """
    success = serializers.BooleanField()
    message = serializers.CharField()
    file_path = serializers.CharField()
    file_name = serializers.CharField()
    product_count = serializers.IntegerField()
    download_url = serializers.CharField(required=False)


class ImportResponseSerializer(serializers.Serializer):
    """
    سریالایزر پاسخ ایمپورت
    """
    success = serializers.BooleanField()
    message = serializers.CharField()
    imported_count = serializers.IntegerField()
    failed_count = serializers.IntegerField()
    errors = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        allow_empty=True
    )


class TemplateResponseSerializer(serializers.Serializer):
    """
    سریالایزر پاسخ فایل نمونه
    """
    success = serializers.BooleanField()
    message = serializers.CharField()
    file_path = serializers.CharField()
    file_name = serializers.CharField()
    download_url = serializers.CharField(required=False)


# ===== Product Excel Row Serializer (for validation) ===== #
class ProductExcelRowSerializer(serializers.Serializer):
    """
    سریالایزر برای اعتبارسنجی هر سطر از فایل Excel در ایمپورت
    """
    id = serializers.IntegerField(required=False, allow_null=True)
    name = serializers.CharField(max_length=150, required=True)
    description = serializers.CharField(required=False, allow_blank=True)
    price = serializers.DecimalField(max_digits=12, decimal_places=0, required=False, default=0)
    show_price = serializers.DecimalField(max_digits=14, decimal_places=0, required=False, default=0)
    price_per_unit = serializers.IntegerField(required=False, default=0)
    has_quantity = serializers.BooleanField(required=False, default=True)
    is_active = serializers.BooleanField(required=False, default=True)
    
    def validate_name(self, value):
        """اعتبارسنجی نام محصول"""
        if not value or not value.strip():
            raise serializers.ValidationError("نام محصول نمی‌تواند خالی باشد.")
        return value.strip()
    
    def validate_price(self, value):
        """اعتبارسنجی قیمت"""
        if value and value < 0:
            raise serializers.ValidationError("قیمت نمی‌تواند منفی باشد.")
        return value