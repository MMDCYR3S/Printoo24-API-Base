import logging

from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone
from django.db import transaction

from .models import(
    ProductCategoryRelation, Product,
    product_code_generator, OrderStateLog,
    OrderStatusGroup, Role, Order, UserRole,
    User, Quotation, Invoice
)

logger = logging.getLogger(__name__)

# =========== GENERATE CORE ON RELATION CREATION =========== #
@receiver(post_save, sender=ProductCategoryRelation)
def generate_code_on_relation_creation(sender, instance, created, **kwargs):
    """
    این سیگنال دقیقاً زمانی اجرا می‌شود که یک دسته‌بندی به محصول اختصاص داده شود.
    """
    
    product = instance.product
    category = instance.category
    
    if not product.code: 
        
        # ===== دریافت دسته بندی اصلی ===== #
        root_category = category.get_root()
        category_slug = root_category.slug
        
        # ===== تولید کد ===== #
        year = timezone.now().year
        new_code = product_code_generator(category_slug, product.slug, year)
        
        # ===== ذخیره کد ===== #
        Product.objects.filter(pk=product.pk).update(code=new_code)

# ========== CREATE STATUS GROUP ========== #
@receiver(post_save, sender=Role)
def create_status_group_for_role(sender, created, instance, **kwargs):
    """
    ایجاد یک گروه‌بندی برای هر نقشی که در سیستم اضافه می‌شود.
    """

    if not instance.slug:
        pass
    
    status_group, group_created = OrderStatusGroup.objects.get_or_create(
        code=instance.slug,
        defaults={'name': instance.name}
    )
    instance.allowed_groups.add(status_group)
    
    if not group_created and status_group.name != instance.name:
        status_group.name = instance.name
        status_group.save()

    if status_group:
        instance.allowed_groups.add(status_group)

# ===== TRACK STATUS CHANGE (PRE-SAVE) ===== #
@receiver(pre_save, sender=Order)
def capture_old_status(sender, instance, **kwargs):
    """
    چرایی: قبل از ذخیره، وضعیت فعلی دیتابیس را می‌گیریم تا بدانیم وضعیت قبلی چه بوده.
    """
    if instance.pk:
        try:
            old_obj = Order.objects.get(pk=instance.pk)
            instance._old_status = old_obj.current_status
        except Order.DoesNotExist:
            instance._old_status = None
    else:
        instance._old_status = None

# ===== LOG STATUS CHANGE (POST-SAVE) ===== #
@receiver(post_save, sender=Order)
def log_order_state_change(sender, instance, created, **kwargs):
    """
    چرایی: بعد از ذخیره، اگر وضعیت تغییر کرده بود، یک رکورد در تاریخچه ثبت می‌کنیم.
    """
    old_status = getattr(instance, '_old_status', None)
    new_status = instance.current_status

    if created or (old_status and old_status != new_status):
        
        # ===== دریافت عامل تغییر (The Logic Fix) ===== #
        actor = getattr(instance, '_status_changer', None)
        
        description = getattr(instance, '_change_reason', None)
        
        if not description:
            if created:
                description = "ثبت اولیه سفارش"
            else:
                from_text = old_status.name if old_status else "نامشخص"
                to_text = new_status.name if new_status else "نامشخص"
                description = f"تغییر وضعیت سیستمی از {from_text} به {to_text}"

        if actor: 
             OrderStateLog.objects.create(
                order=instance,
                from_status=old_status,
                to_status=new_status,
                actor=actor,
                description=description
            )
        else:
            pass

# ===== سیگنال تخصیص نقش پیش‌فرض (مشتری) به کاربر جدید ===== #
@receiver(post_save, sender=User, dispatch_uid="assign_customer_role_on_new_user")
def assign_default_role_to_new_user(sender, instance, created, **kwargs):
    """
    این سیگنال به محض ایجاد یک کاربر جدید در سیستم فراخوانی می‌شود.
    اگر کاربر ادمین یا کارمند نباشد، نقش 'مشتری' به صورت خودکار به او اختصاص می‌یابد.
    """
    
    # ===== بررسی اینکه آیا کاربر جدید است و ادمین/کارمند نیست ===== #
    if created and not instance.is_superuser and not instance.is_staff:
        
        # ===== استفاده از تراکنش برای حفظ یکپارچگی دیتابیس ===== #
        with transaction.atomic():
            try:
                # ===== 1. دریافت نقش مشتری (اگر نبود، با این مشخصات ساخته می‌شود) ===== #
                customer_role, role_created = Role.objects.get_or_create(
                    slug='customer',
                    defaults={
                        'name': 'مشتری',
                        'type': 'normal',
                        'is_customer': True
                    }
                )
                
                if role_created:
                    logger.info("نقش 'مشتری' در سیستم وجود نداشت و به صورت خودکار ایجاد شد.")

                # ===== 2. اختصاص نقش به کاربر (در جدول واسط UserRole) ===== #
                UserRole.objects.get_or_create(
                    user=instance,
                    role=customer_role
                )
                
                logger.info(f"نقش 'مشتری' با موفقیت به کاربر {instance.phone_number} اختصاص یافت.")
                
            except Exception as e:
                # ===== لاگ کردن خطا در صورت بروز مشکل سیستمی ===== #
                logger.error(f"خطا در تخصیص نقش مشتری به کاربر {instance.phone_number}: {str(e)}")

# ===== SYNC ORDER TOTAL PRICE TO QUOTATION (PRE-SAVE) ===== #
@receiver(pre_save, sender=Order)
def capture_old_total_price(sender, instance, **kwargs):
    """
    قبل از ذخیره، مبلغ کل فعلی دیتابیس را نگه می‌داریم
    تا در post_save بتوانیم تغییر را تشخیص دهیم.
    """
    if instance.pk:
        try:
            old_obj = Order.objects.get(pk=instance.pk)
            instance._old_total_price = old_obj.total_price
        except Order.DoesNotExist:
            instance._old_total_price = None
    else:
        instance._old_total_price = None


# ===== SYNC ORDER TOTAL PRICE TO QUOTATION (POST-SAVE) ===== #
@receiver(post_save, sender=Order, dispatch_uid="sync_order_price_to_quotation")
def sync_total_price_to_quotation(sender, instance, created, **kwargs):
    """
    اگر ادمین مبلغ کل سفارش را تغییر داد، پیش‌فاکتور مرتبط هم آپدیت می‌شود.
    فقط روی سفارش‌هایی که قبلاً ساخته شده‌اند اجرا می‌شود (not created).
    """
    if created:
        return

    old_price = getattr(instance, '_old_total_price', None)

    # ===== اگر قیمت تغییر نکرده، کاری صورت نگیرد ===== #
    if old_price is None or old_price == instance.total_price:
        return

    try:
        quotation = instance.origin_quotation
        if quotation:
            Quotation.objects.filter(pk=quotation.pk).update(
                total_price=instance.total_price
            )
            logger.info(
                f"Quotation #{quotation.quotation_number} total_price synced "
                f"from {old_price} to {instance.total_price} "
                f"(Order: {instance.order_code})"
            )
    except Quotation.DoesNotExist:
        pass
    except Exception as e:
        logger.error(f"Error syncing price to quotation for Order {instance.pk}: {e}")

# ===== SYNC INVOICE TO ORDER (PRE-SAVE) ===== #
@receiver(pre_save, sender=Invoice)
def capture_old_invoice_amount(sender, instance, **kwargs):
    """
    نگه‌داشتن مبلغ نهایی قبلی فاکتور برای مقایسه
    """
    if instance.pk:
        try:
            old_obj = Invoice.objects.get(pk=instance.pk)
            instance._old_final_amount = old_obj.final_amount
        except Invoice.DoesNotExist:
            instance._old_final_amount = None
    else:
        instance._old_final_amount = None


# ===== SYNC INVOICE TO ORDER (POST-SAVE) ===== #
@receiver(post_save, sender=Invoice, dispatch_uid="sync_invoice_amount_to_order")
def sync_invoice_amount_to_order(sender, instance, created, **kwargs):
    """
    اگر قیمت نهایی فاکتور تغییر کرد، قیمت کل سفارش برابر با آن می‌شود.
    """
    # ===== بررسی تغییر قیمت ===== #
    if not created:
        old_amount = getattr(instance, '_old_final_amount', None)
        if old_amount is None or old_amount == instance.final_amount:
            return

    if instance.order_id:
        Order.objects.filter(pk=instance.order_id).update(
            total_price=instance.final_amount
        )
        logger.info(f"Order #{instance.order_id} total_price synced to matches Invoice #{instance.invoice_number}.")

# ===== SYNC ORDER TO INVOICE (POST-SAVE) ===== #
@receiver(post_save, sender=Order, dispatch_uid="sync_order_price_to_invoice")
def sync_total_price_to_invoice(sender, instance, created, **kwargs):
    """
    اگر قیمت کل سفارش تغییر کرد:
    ۱. برای افزایش قیمت: مستقیما به مبلغ اقلام اضافه می‌شود.
    ۲. برای کاهش قیمت (آبشاری): خدمات -> مالیات -> اقلام (تا حد پایه) -> تخفیف (در صورت نیاز).
    """
    if created:
        return

    old_price = getattr(instance, '_old_total_price', None)
    if old_price is None or old_price == instance.total_price:
        return

    price_difference = instance.total_price - old_price

    if hasattr(instance, 'invoice') and instance.invoice:
        invoice = instance.invoice
        
        new_items = invoice.items_amount or 0
        new_services = invoice.services_amount or 0
        new_tax = invoice.tax_amount or 0
        new_discount = invoice.discount_amount or 0
        
        if price_difference > 0:
            # ===== در صورت افزایش قیمت، به مبلغ اقلام اضافه می‌شود ===== #
            new_items += price_difference
        else:
            # ===== در صورت کاهش قیمت، منطق آبشاری اجرا می‌شود ===== #
            reduction = abs(price_difference)
            
            # ===== کسر از خدمات ===== #
            svc_deduct = min(new_services, reduction)
            new_services -= svc_deduct
            reduction -= svc_deduct
            
            # ===== کسر از مالیات ===== #
            tax_deduct = min(new_tax, reduction)
            new_tax -= tax_deduct
            reduction -= tax_deduct
            
            # ===== کسر از اقلام (با شرط حفظ حداقل قیمت پایه محصولات) ===== #
            min_items_allowed = instance.base_products_price or 0
            if new_items > min_items_allowed and reduction > 0:
                max_item_deductible = new_items - min_items_allowed
                items_deduct = min(max_item_deductible, reduction)
                new_items -= items_deduct
                reduction -= items_deduct
                
            # ===== در صورتی که هنوز کاهش قیمت نیاز است (رسیدن به کف اقلام)، به تخفیف اضافه می‌شود ===== #
            if reduction > 0:
                new_discount += reduction

        # ===== آپدیت دیتابیس (بدون تریگر کردن سیگنال‌های فاکتور برای جلوگیری از لوپ) ===== #
        Invoice.objects.filter(pk=invoice.pk).update(
            items_amount=new_items,
            services_amount=new_services,
            tax_amount=new_tax,
            discount_amount=new_discount,
            final_amount=instance.total_price
        )
        
        logger.info(f"Invoice #{invoice.invoice_number} cascaded sync. New Final: {instance.total_price}")

# ===== AUTO-BALANCE INVOICE AMOUNTS (PRE-SAVE) ===== #
@receiver(pre_save, sender=Invoice, dispatch_uid="auto_balance_invoice_amounts")
def auto_balance_invoice_amounts(sender, instance, **kwargs):
    """
    تراز کردن خودکار فاکتور:
    هر زمان که یکی از اجزای فاکتور (اقلام، خدمات و...) تغییر کند،
    مبلغ نهایی (final_amount) بر اساس جمع آن‌ها به صورت خودکار بازنویسی می‌شود.
    """
    items_amt = instance.items_amount or 0
    services_amt = instance.services_amount or 0
    tax_amt = instance.tax_amount or 0
    discount_amt = instance.discount_amount or 0

    # ===== محاسبه مبلغ نهایی قطعی ===== #
    expected_final = (items_amt + services_amt + tax_amt) - discount_amt

    if instance.final_amount != expected_final:
        instance.final_amount = expected_final
        logger.info(f"Invoice {instance.invoice_number} final_amount auto-calculated to: {expected_final}")
