import random
import uuid
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone

# ===== ایمپورت مدل‌های مورد نیاز ===== #
from core.models import (
    Product, Order, OrderItem, OrderItemFile,
    OrderStatus, OrderStatusGroup, Address, Province, City,
    ProductOption, ProductSize, ProductQuantity,
    ProductFileUploadRequirement
)

User = get_user_model()

class Command(BaseCommand):
    help = 'Generates 10 realistic ORDERS with full product details & files.'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING('>>> Start seeding orders...'))

        # 1. پیدا کردن یا ساخت کاربر (ادمین یا اولین کاربر)
        user = User.objects.filter(is_superuser=True).first()
        if not user:
            # اگر هیچ کاربری نبود، بساز
            if not User.objects.exists():
                user = User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
                self.stdout.write(self.style.SUCCESS("User 'admin' created."))
            else:
                user = User.objects.first()
        
        self.stdout.write(f"Using user: {user.username}")

        # 2. اطمینان از وجود آدرس (اگر ندارد، بساز)
        address = self.ensure_address(user)

        # 3. اطمینان از وجود وضعیت‌های سفارش
        initial_status = self.ensure_order_statuses()

        # 4. دریافت محصولات
        products = list(Product.objects.filter(is_active=True))
        if not products:
            self.stdout.write(self.style.ERROR("هیچ محصولی یافت نشد. لطفا ابتدا seed_products را اجرا کنید."))
            return

        # 5. ایجاد سفارشات
        with transaction.atomic():
            for i in range(1, 11):
                self.create_full_order(user, address, initial_status, products, i)

        self.stdout.write(self.style.SUCCESS('✅ Successfully added 10 ORDERS with full details.'))

    def ensure_address(self, user):
        """ اگر کاربر آدرس ندارد، یک آدرس پیش‌فرض می‌سازد """
        addr = Address.objects.filter(user=user).first()
        if addr:
            return addr
        
        self.stdout.write(self.style.WARNING("User has no address. Creating default address..."))
        
        # اطمینان از وجود استان و شهر
        province, _ = Province.objects.get_or_create(name="تهران", defaults={'slug': 'tehran'})
        city, _ = City.objects.get_or_create(name="تهران", province=province, defaults={'slug': 'tehran-city'})
        
        addr = Address.objects.create(
            user=user,
            province=province,
            city=city,
            postal_code="1234567890",
            address="تهران، میدان آزادی، خیابان آزادی، پلاک ۱۱۰"
        )
        return addr

    def ensure_order_statuses(self):
        """ ایجاد وضعیت‌های پایه اگر وجود ندارند """
        group, _ = OrderStatusGroup.objects.get_or_create(
            code='sales', defaults={'name': 'واحد فروش'}
        )
        
        status, created = OrderStatus.objects.get_or_create(
            internal_code='PENDING_REVIEW_SALES',
            defaults={
                'name': 'در انتظار بررسی',
                'group': group,
                'status_type': 'initial',
                'sort_order': 1
            }
        )
        return status

    def create_full_order(self, user, address, status, products, index):
        """ ساخت یک سفارش کامل با یک آیتم و فایل‌های مربوطه """
        
        # --- الف) انتخاب محصول و جزئیات ---
        product = random.choice(products)
        
        # 1. آپشن‌ها (با جزئیات کامل برای JSON)
        selected_options_data = []
        product_options = ProductOption.objects.filter(product=product).select_related('option')
        
        for prod_opt in product_options:
            if prod_opt.is_required or random.choice([True, False]):
                choices = list(prod_opt.choices.all())
                if choices:
                    selected_val = random.choice(choices)
                    selected_options_data.append({
                        "id": selected_val.id, # ID مقدار انتخاب شده
                        "option_id": prod_opt.option.id, # ID ویژگی
                        "option_name": prod_opt.option.label, # نام ویژگی
                        "value_label": selected_val.label, # نام مقدار
                        "price_impact": float(selected_val.price_impact) # قیمت افزوده
                    })

        # 2. سایز و ابعاد
        pricing_config = getattr(product, 'pricing_config', None)
        is_custom_size = False
        
        if pricing_config and pricing_config.accepts_custom_dimensions:
            is_custom_size = random.choice([True, False]) 
        
        size_id = None
        size_name = None
        width = None
        height = None

        if is_custom_size:
            width = round(random.uniform(50, 500), 1)
            height = round(random.uniform(50, 300), 1)
        else:
            available_sizes = list(ProductSize.objects.filter(product=product).select_related('size'))
            if available_sizes:
                selected_size = random.choice(available_sizes)
                size_id = selected_size.size.id
                size_name = selected_size.size.name

        # 3. تیراژ
        quantity = 1000
        if is_custom_size:
            quantity = random.randint(1, 20)
        else:
            quants = list(ProductQuantity.objects.filter(product=product))
            if quants:
                quantity = random.choice(quants).quantity.value
            else:
                quantity = random.choice([500, 1000, 2000, 5000])

        # --- ب) محاسبه قیمت ---
        base_price = float(product.price)
        options_price = sum(opt['price_impact'] for opt in selected_options_data)
        unit_price = base_price + options_price
        if unit_price <= 0: unit_price = 15000 # قیمت پایه (اگر رایگان بود)
        
        total_line_price = Decimal(unit_price * quantity)

        # --- ج) ساخت سفارش (Header) ---
        order_code = f"ORD-{timezone.now().year}-{random.randint(10000, 99999)}"
        
        order = Order.objects.create(
            user=user,
            order_code=order_code,
            type='2', # سفارش اختصاصی
            current_status=status,
            address=address,
            total_price=total_line_price,
            base_products_price=total_line_price,
            description=f"سفارش تستی شماره {index}"
        )

        # --- د) ساخت آیتم سفارش (Line Item) ---
        # ساختار JSON دقیقاً مشابه سبد خرید
        item_json_data = {
            "quantity": quantity,
            "size_id": size_id,
            "size_name": size_name,
            "width": width,
            "height": height,
            "options": selected_options_data, # <--- جزئیات دقیق آپشن‌ها
            "has_design": True
        }

        order_item = OrderItem.objects.create(
            order=order,
            product=product,
            quantity=quantity,
            price=total_line_price, # قیمت کل این ردیف
            items=item_json_data,
            admin_note="تولید فوری لطفا"
        )

        # --- ه) ساخت فایل‌های طراحی (Order Item Files) ---
        requirements = ProductFileUploadRequirement.objects.filter(product=product)
        
        for req in requirements:
            # ایجاد رکورد فایل
            OrderItemFile.objects.create(
                order_item=order_item,
                requirement=req,
                file=f"orders/designs/dummy_{uuid.uuid4().hex[:8]}.jpg", 
                version=1,
                is_latest=True,
                is_accepted=False
            )

        self.stdout.write(f" + Created Order {order_code} with Item: {product.name}")
