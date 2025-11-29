import random
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from core.models import (
    ProductCategory, Product, Size, ProductSize, 
    Material, ProductMaterial, Quantity, ProductQuantity,
    Option, OptionValue, ProductOption,
    FileUploadSpec, ProductFileUploadRequirement
)

User = get_user_model()

class Command(BaseCommand):
    help = 'Seeds the database with initial product data'

    def handle(self, *args, **kwargs):
        self.stdout.write('Seeding data...')
        create_full_test_data()
        self.stdout.write(self.style.SUCCESS('Successfully seeded data'))

def create_full_test_data():
    # 1. ادمین سیستم
    admin_user, _ = User.objects.get_or_create(
        email="admin@printoo24.com",
        defaults={'username': 'admin2', 'is_staff': True, 'is_superuser': True}
    )
    if _: admin_user.set_password("admin123"); admin_user.save()

    # ==========================================
    # 2. ویژگی‌های پایه (Attributes)
    # ==========================================
    
    # --- سایزها ---
    sizes = {
        'bc_std': Size.objects.create(name="8.5x4.8 (استاندارد)", width=8.5, height=4.8, user=admin_user),
        'bc_sqr': Size.objects.create(name="5.5x5.5 (مربعی)", width=5.5, height=5.5, user=admin_user),
        'a4': Size.objects.create(name="A4", width=21.0, height=29.7, user=admin_user),
        'a5': Size.objects.create(name="A5", width=14.8, height=21.0, user=admin_user),
    }

    # --- جنس‌ها ---
    mats = {
        'glossy_300': Material.objects.create(name="گلاسه ۳۰۰ گرم", user=admin_user),
        'matte_300': Material.objects.create(name="کتان ۳۰۰ گرم", user=admin_user),
        'glossy_135': Material.objects.create(name="گلاسه ۱۳۵ گرم (تحریر)", user=admin_user),
        'banner_13oz': Material.objects.create(name="بنر ۱۳ اونس", user=admin_user),
        'flex': Material.objects.create(name="فلکس", user=admin_user),
    }

    # --- تیراژها ---
    qtys = {
        '1000': Quantity.objects.create(value=1000, user=admin_user),
        '2000': Quantity.objects.create(value=2000, user=admin_user),
        '5000': Quantity.objects.create(value=5000, user=admin_user),
        '1': Quantity.objects.create(value=1, user=admin_user), # برای بنر
    }

    # --- آپشن‌ها ---
    opt_corner = Option.objects.create(name="نوع گوشه", user=admin_user)
    val_sharp = OptionValue.objects.create(option=opt_corner, value="تیز", user=admin_user)
    val_round = OptionValue.objects.create(option=opt_corner, value="گرد", user=admin_user)

    opt_cover = Option.objects.create(name="روکش", user=admin_user)
    val_uv = OptionValue.objects.create(option=opt_cover, value="یووی موضعی", user=admin_user)
    val_cell = OptionValue.objects.create(option=opt_cover, value="سلفون مات", user=admin_user)

    opt_punch = Option.objects.create(name="پانچ", user=admin_user) # برای بنر
    val_4cor = OptionValue.objects.create(option=opt_punch, value="۴ گوشه", user=admin_user)
    val_no = OptionValue.objects.create(option=opt_punch, value="بدون پانچ", user=admin_user)

    # --- مشخصات فایل ---
    spec_front = FileUploadSpec.objects.create(name="طرح رو", description="فایل JPG/TIFF روی کار")
    spec_back = FileUploadSpec.objects.create(name="طرح پشت", description="فایل JPG/TIFF پشت کار")
    spec_uv = FileUploadSpec.objects.create(name="فایل UV", description="فایل سیاه و سفید برای یووی")

    # ==========================================
    # 3. دسته‌بندی‌ها (Categories)
    # ==========================================
    cat_root_bc = ProductCategory.objects.create(name="کارت ویزیت", user=admin_user)
    cat_bc_fancy = ProductCategory.objects.create(name="کارت ویزیت فانتزی", parent=cat_root_bc, user=admin_user)
    cat_bc_eco = ProductCategory.objects.create(name="کارت ویزیت ارزان", parent=cat_root_bc, user=admin_user)

    cat_root_flyer = ProductCategory.objects.create(name="تراکت و پوستر", user=admin_user)
    
    cat_root_lfp = ProductCategory.objects.create(name="چاپ عریض (بنر)", user=admin_user)

    # ==========================================
    # 4. محصولات (Products)
    # ==========================================

    # --- محصول ۱: کارت ویزیت ساده (ارزان) ---
    p1 = Product.objects.create(
        name="کارت ویزیت گلاسه براق",
        category=cat_bc_eco,
        user=admin_user,
        description="ارزان‌ترین کارت ویزیت بازار",
        has_quantity=True
    )
    # اتصال ویژگی‌ها
    ProductSize.objects.create(product=p1, size=sizes['bc_std'], user=admin_user, price_impact=0)
    ProductMaterial.objects.create(product=p1, material=mats['glossy_300'], user=admin_user, price_impact=0)
    ProductQuantity.objects.create(product=p1, quantity=qtys['1000'], user=admin_user, price=180000)
    ProductQuantity.objects.create(product=p1, quantity=qtys['2000'], user=admin_user, price=350000)
    # فایل: فقط رو (اجباری) و پشت (اختیاری)
    ProductFileUploadRequirement.objects.create(product=p1, spec=spec_front, is_required=True, sort_order=1)
    ProductFileUploadRequirement.objects.create(product=p1, spec=spec_back, is_required=False, sort_order=2)

    # --- محصول ۲: کارت ویزیت کتان (فانتزی) ---
    p2 = Product.objects.create(
        name="کارت ویزیت کتان آلمان",
        category=cat_bc_fancy,
        user=admin_user,
        description="بافت‌دار و شیک",
        has_quantity=True
    )
    ProductSize.objects.create(product=p2, size=sizes['bc_std'], user=admin_user, price_impact=0)
    ProductSize.objects.create(product=p2, size=sizes['bc_sqr'], user=admin_user, price_impact=20000) # گرونتر برای سایز خاص
    ProductMaterial.objects.create(product=p2, material=mats['matte_300'], user=admin_user, price_impact=50000)
    ProductQuantity.objects.create(product=p2, quantity=qtys['1000'], user=admin_user, price=450000)
    # آپشن: گوشه گرد یا تیز
    ProductOption.objects.create(product=p2, option=opt_corner, option_value=val_sharp, user=admin_user, price_impact=0)
    ProductOption.objects.create(product=p2, option=opt_corner, option_value=val_round, user=admin_user, price_impact=30000)
    # فایل: رو و پشت اجباری
    ProductFileUploadRequirement.objects.create(product=p2, spec=spec_front, is_required=True, sort_order=1)
    ProductFileUploadRequirement.objects.create(product=p2, spec=spec_back, is_required=True, sort_order=2)

    # --- محصول ۳: کارت ویزیت لمینت برجسته (پیچیده) ---
    p3 = Product.objects.create(
        name="کارت ویزیت لمینت برجسته طلاکوب",
        category=cat_bc_fancy,
        user=admin_user,
        description="لوکس‌ترین کارت موجود",
        has_quantity=True
    )
    ProductSize.objects.create(product=p3, size=sizes['bc_std'], user=admin_user)
    ProductMaterial.objects.create(product=p3, material=mats['glossy_300'], user=admin_user)
    ProductQuantity.objects.create(product=p3, quantity=qtys['1000'], user=admin_user, price=950000)
    # فایل: رو، پشت، و فایل UV اجباری
    ProductFileUploadRequirement.objects.create(product=p3, spec=spec_front, is_required=True, sort_order=1)
    ProductFileUploadRequirement.objects.create(product=p3, spec=spec_back, is_required=True, sort_order=2)
    ProductFileUploadRequirement.objects.create(product=p3, spec=spec_uv, is_required=True, sort_order=3)

    # --- محصول ۴: تراکت (چند سایز) ---
    p4 = Product.objects.create(
        name="تراکت گلاسه",
        category=cat_root_flyer,
        user=admin_user,
        description="پخش عمومی",
        has_quantity=True
    )
    ProductSize.objects.create(product=p4, size=sizes['a4'], user=admin_user, price_impact=200000)
    ProductSize.objects.create(product=p4, size=sizes['a5'], user=admin_user, price_impact=0) # قیمت پایه بر اساس A5
    ProductMaterial.objects.create(product=p4, material=mats['glossy_135'], user=admin_user)
    ProductQuantity.objects.create(product=p4, quantity=qtys['5000'], user=admin_user, price=1200000)
    ProductFileUploadRequirement.objects.create(product=p4, spec=spec_front, is_required=True)

    # --- محصول ۵: بنر (ابعاد دلخواه) ---
    p5 = Product.objects.create(
        name="چاپ بنر تسلیت/تبلیغاتی",
        category=cat_root_lfp,
        user=admin_user,
        description="چاپ با دستگاه سالونت",
        accepts_custom_dimensions=True, # <--- نکته مهم
        price_per_square_unit=150000,   # متری 150 هزار تومان
        has_quantity=False              # معمولا تیراژ ندارد، متراژ دارد
    )
    # بنر سایز ثابت ندارد، فقط جنس دارد
    ProductMaterial.objects.create(product=p5, material=mats['banner_13oz'], user=admin_user)
    ProductMaterial.objects.create(product=p5, material=mats['flex'], user=admin_user, price_impact=50000) # فلکس گرونتره
    # برای بنر، آبجکت Quantity معمولا 1 است
    ProductQuantity.objects.create(product=p5, quantity=qtys['1'], user=admin_user, price=0) 
    
    # آپشن پانچ
    ProductOption.objects.create(product=p5, option=opt_punch, option_value=val_4cor, user=admin_user, price_impact=10000)
    ProductOption.objects.create(product=p5, option=opt_punch, option_value=val_no, user=admin_user, price_impact=0)
    
    ProductFileUploadRequirement.objects.create(product=p5, spec=spec_front, is_required=True)

    print(f"Created 5 products with full specs.")