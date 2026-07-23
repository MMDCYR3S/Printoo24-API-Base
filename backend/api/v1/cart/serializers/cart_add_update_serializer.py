from rest_framework import serializers

# ===== Add To Cart Serializer ===== #
class AddToCartSerializer(serializers.Serializer):
    product_id = serializers.IntegerField(required=True, help_text="شناسه محصولی که قرار است به سبد اضافه شود")
    
    # استفاده از DictField برای دریافت ساختار کاملاً داینامیک فیلدساز
    selections = serializers.DictField(
        child=serializers.JSONField(), # به کلاینت اجازه می‌دهد عدد، رشته یا لیست (برای چک‌باکس‌ها) بفرستد
        help_text="""
        دیکشنری انتخاب‌های کاربر.
        - کلیدها: آیدی فیلدهای داینامیک (مثلاً "10")
        - مقادیر: مقدار تایپ شده یا آیدیِ گزینه انتخاب شده.
        - فیلدهای رزرو شده (اختیاری): "name" (نام پروژه) و "description" (توضیحات مشتری).
        """
    )

    def validate_selections(self, value):
        """
        اینجا یک گارد اولیه می‌گذاریم تا مطمئن شویم فرانت‌اند دیتای پرت‌وپلا نمی‌فرستد.
        ولیدیشن اصلی و وابستگی‌ها در Domain Service (CartProcessor) انجام می‌شود.
        """
        if not isinstance(value, dict):
            raise serializers.ValidationError("فرمت selections باید یک آبجکت JSON (دیکشنری) باشد.")
        return value

# ===== Cart Item Update Serializer ===== #
class CartItemUpdateSerializer(serializers.Serializer):
    # در زمان آپدیت، نیازی به product_id نیست، چون خود آیتم مشخص است
    selections = serializers.DictField(
        child=serializers.JSONField(),
        help_text="دیکشنری آپدیت شده از انتخاب‌های کاربر. هر چیزی که بفرستید، جایگزین قبلی می‌شود و قیمت مجدداً محاسبه می‌گردد."
    )