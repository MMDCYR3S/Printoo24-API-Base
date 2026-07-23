import random
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction

# ===== ایمپورت مدل‌های مورد نیاز ===== #
from core.models import (
    Product, Cart, CartItem, 
    ProductOption, ProductOptionValue, 
    ProductSize, ProductQuantity
)

User = get_user_model()

class Command(BaseCommand):
    help = 'Adds 10 realistic items to the user cart with FULL option details.'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING('>>> Start seeding cart items...'))

        # 1. پیدا کردن کاربر
        user = User.objects.filter(is_superuser=True).first()
        if not user:
            user = User.objects.first()
        
        if not user:
            self.stdout.write(self.style.ERROR("هیچ کاربری در سیستم یافت نشد. ابتدا یک کاربر بسازید."))
            return

        self.stdout.write(f"User found: {user.username}")

        # 2. پیدا کردن یا ساخت سبد خرید
        cart, created = Cart.objects.get_or_create(user=user)
        if created:
            self.stdout.write(self.style.SUCCESS(f"Created new cart for {user.username}"))
        else:
            self.stdout.write(f"Using existing cart ID: {cart.id}")

        # 3. دریافت محصولات فعال
        products = list(Product.objects.filter(is_active=True))
        if not products:
            self.stdout.write(self.style.ERROR("هیچ محصول فعالی یافت نشد. ابتدا دستور seed_products را اجرا کنید."))
            return

        # 4. ایجاد ۱۰ آیتم تصادفی
        with transaction.atomic():
            # پاک کردن آیتم‌های قبلی برای تمیزی تست (اختیاری)
            # CartItem.objects.filter(cart=cart).delete()
            
            for i in range(1, 11):
                product = random.choice(products)
                self.create_cart_item(cart, product, i)

        self.stdout.write(self.style.SUCCESS('✅ Successfully added 10 items to the cart with FULL details.'))

    def create_cart_item(self, cart, product, index):
        """
        ساخت یک آیتم سبد خرید با جزئیات کامل (نام آپشن، نام مقدار و ...)
        """
        # --- الف) تعیین ویژگی‌های انتخابی (Options) با جزئیات کامل ---
        selected_option_value_ids = []
        detailed_options = [] # لیست دیکشنری‌ها برای ذخیره در JSON
        
        # تمام آپشن‌های متصل به این محصول را می‌گیریم
        product_options = ProductOption.objects.filter(product=product).select_related('option')
        
        for prod_opt in product_options:
            # انتخاب تصادفی یک مقدار برای هر آپشن
            if prod_opt.is_required or random.choice([True, False]):
                choices = list(prod_opt.choices.all()) # ProductOptionValue
                if choices:
                    selected_val = random.choice(choices)
                    selected_option_value_ids.append(selected_val.id)
                    
                    # ذخیره جزئیات کامل برای JSON
                    detailed_options.append({
                        "id": selected_val.id, # ID مقدار انتخاب شده
                        "option_id": prod_opt.option.id, # ID آپشن اصلی
                        "option_name": prod_opt.option.label, # نام آپشن (مثلاً: جنس کاغذ)
                        "value_label": selected_val.label, # مقدار انتخاب شده (مثلاً: گلاسه ۳۰۰ گرم)
                        "price_impact": float(selected_val.price_impact) # تاثیر قیمت
                    })

        # --- ب) تعیین سایز و ابعاد ---
        pricing_config = getattr(product, 'pricing_config', None)
        is_custom_size = False
        
        if pricing_config and pricing_config.accepts_custom_dimensions:
            is_custom_size = random.choice([True, False, False]) 

        size_id = None
        size_name = None # برای ذخیره نام سایز
        custom_width = None
        custom_height = None

        if is_custom_size:
            custom_width = round(random.uniform(50, 500), 1)
            custom_height = round(random.uniform(50, 300), 1)
        else:
            available_sizes = list(ProductSize.objects.filter(product=product).select_related('size'))
            if available_sizes:
                selected_size = random.choice(available_sizes)
                size_id = selected_size.size.id
                size_name = selected_size.size.name # نام سایز (مثلاً: A4)

        # --- ج) تعیین تیراژ (Quantity) ---
        quantity = 1000
        if is_custom_size:
            quantity = random.randint(1, 50)
        else:
            available_quantities = list(ProductQuantity.objects.filter(product=product))
            if available_quantities:
                quantity = random.choice(available_quantities).quantity.value
            else:
                quantity = random.choice([500, 1000, 2000, 5000])

        # --- د) ساخت ساختار JSON کامل (selections) ---
        # این ساختار شامل هم IDها (برای لاجیک بک‌اند) و هم نام‌ها (برای نمایش فرانت) است
        selections_data = {
            "quantity": quantity,
            "size_id": size_id,
            "size_name": size_name, # اضافه شد
            "width": custom_width,
            "height": custom_height,
            "option_value_ids": selected_option_value_ids, # فقط ID ها
            "options": detailed_options, # <--- لیست کامل دیکشنری‌ها اضافه شد
            "has_design": True
        }

        # --- ه) محاسبه قیمت شماتیک ---
        # محاسبه ساده: قیمت پایه + جمع قیمت آپشن‌ها
        base_price = float(product.price)
        options_price = sum(opt['price_impact'] for opt in detailed_options)
        dummy_unit_price = base_price + options_price
        if dummy_unit_price == 0: dummy_unit_price = 10000 # قیمت کف
        
        final_price = Decimal(dummy_unit_price * quantity)

        # --- و) ذخیره آیتم ---
        CartItem.objects.create(
            cart=cart,
            product=product,
            quantity=quantity,
            price=final_price,
            items={"selections": selections_data} 
        )
        
        self.stdout.write(f" + Added item {index}: {product.name} (Qty: {quantity})")