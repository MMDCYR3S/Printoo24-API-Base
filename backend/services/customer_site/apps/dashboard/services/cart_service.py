import logging
from typing import Dict, Any

from django.db import transaction
from django.db.models import Count, Sum, F, Prefetch
from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError

from core.models import (
    User,
    Product,
    ProductMaterial,
    ProductSize,
    ProductOptionValue,
    Cart,
    CartItem,
)
from core.domain.cart import CartDomainService
from core.domain.product import ProductDomainService

# ===== Logger ===== #
logger = logging.getLogger("dashboard.services.cart_dashboard")

# ===== Cart Dashboard Service ===== #
class CartDashboardService:
    def __init__(self):
        self.domain_service = CartDomainService()
        self.product_service = ProductDomainService()

    # ===== مدیریت سبد خرید (Cart Management) ===== #
    
    def get_user_cart_details(self, user_id: int):
        """ دریافت جزئیات کامل سبد خرید یک کاربر خاص """
        logger.info(f"START: Get Cart Details for User ID {user_id}")
        
        try:
            user = get_object_or_404(User, pk=user_id)
            cart = self.domain_service.get_or_create_cart_for_user(user)
            
            # ===== بهینه سازی ===== #
            cart_queryset = Cart.objects.filter(id=cart.id).prefetch_related(
                Prefetch(
                    'cart_items',
                    queryset=CartItem.objects.select_related('product').prefetch_related(
                        'uploads__requirement__spec'
                    )
                )
            ).first()
            
            logger.info(f"SUCCESS: Cart details retrieved for User {user_id}. Cart ID: {cart.id}")
            
            return {
                'cart': cart_queryset,
                'user': user
            }
        except Exception as e:
            logger.error(f"FAILED: Get Cart Details for User {user_id}. Error: {str(e)}", exc_info=True)
            raise e
    def clear_user_cart(self, user_id: int):
        """ خالی کردن سبد خرید کاربر """
        logger.warning(f"START: Clearing Cart for User ID {user_id}")
        try:
            user = get_object_or_404(User, pk=user_id)
            self.domain_service.clear_cart(user)
            logger.info(f"SUCCESS: Cart cleared for User {user_id}")
        except Exception as e:
            logger.error(f"FAILED: Clear Cart for User {user_id}. Error: {str(e)}", exc_info=True)
            raise e

    # ===== مدیریت آیتم‌ها (Item Management) ===== #

    @transaction.atomic
    def add_item_to_user_cart_simple(self, user_id: int, data: Dict[str, Any]):
        """
        افزودن آیتم با فرمت ساده شده.
        data: {product_slug, selections: {...}}
        """
        user = get_object_or_404(User, pk=user_id)
        # ===== دریافت محصول ===== #
        try:
            logger.info(f"START: Get cart of the user #{user_id}")
            product = Product.objects.get(slug=data['product_slug'])
        except Product.DoesNotExist:
            logger.warning(f"Product not found: {data.get('product_slug')}")
            raise ValidationError("محصول یافت نشد.")
        
        selections = data['selections']
        
        # ===== اعتبارسنجی داده‌های ورودی کاربر و محصول ===== #
        specs = self._prepare_specs_simple(product, selections)
        
        # ===== دریافت سبد خرید ===== #
        cart_item = self.domain_service.add_complex_item(
            user=user,
            product=product,
            quantity=selections['quantity'],
            specs=specs
        )
        logger.info(f"SUCCESS: Item {cart_item.id} added to cart for User {user_id}. Price: {cart_item.price}")
        return cart_item
    
    def _prepare_specs_simple(self, product, selections):
        """
        تبدیل ورودی ساده به ساختار specs مورد نیاز دامین.
        """
        
        specs = {
            'has_design': selections.get('has_design', True)
        }

        # --- متریال ---
        try:
            specs['material_obj'] = ProductMaterial.objects.get(
                id=selections['material_id'], 
                product=product
            )
        except ProductMaterial.DoesNotExist:
            raise ValidationError("متریال نامعتبر است.")

        # ===== سایز ===== #
        size_id = selections.get('size_id')
        if size_id:
            try:
                size_obj = ProductSize.objects.get(id=size_id, product=product)
                specs['size_obj'] = size_obj
                specs['width'] = size_obj.size.width
                specs['height'] = size_obj.size.height
            except ProductSize.DoesNotExist:
                raise ValidationError("سایز نامعتبر است.")
        else:
            # ===== ابعاد دلخواه ===== #
            width = selections.get('custom_width')
            height = selections.get('custom_height')
            if not width or not height:
                raise ValidationError("باید یا سایز استاندارد انتخاب کنید یا ابعاد دلخواه وارد کنید.")
            
            specs['width'] = width
            specs['height'] = height
            specs['custom_dimensions'] = {'width': width, 'height': height}

        # ===== گزینه‌های انتخابی ===== #
        option_ids = selections.get('option_value_ids', [])
        if option_ids:
            options = list(ProductOptionValue.objects.filter(
                id__in=option_ids,
                product_option__product=product
            ))
            if len(options) != len(option_ids):
                raise ValidationError("برخی از آپشن‌های انتخابی نامعتبر هستند.")
            specs['option_objs'] = options
        else:
            specs['option_objs'] = []

        return specs

    @transaction.atomic
    def update_cart_item(self, user_id: int, item_id: int, data: Dict[str, Any]):
        """ ویرایش آیتم سبد خرید """
        logger.info(f"START: Update Cart Item {item_id} for User {user_id}")
        
        if 'specs' in data:
            user = get_object_or_404(User, pk=user_id)
            # ===== چک کردن ویژگی هیا محصول ===== #
            item = self.domain_service._item_repo.get_by_id(item_id)
            specs = self._prepare_specs_for_domain(item.product, data['specs'])
            
            logger.debug(f"Updating specs for item {item_id}")
            
            return self.domain_service.update_complex_item(
                user=user,
                item_id=item_id,
                quantity=data.get('quantity', item.quantity),
                specs=specs
            )
        else:
            logger.debug(f"Updating quantity for item {item_id} to {data['quantity']}")
            return self.domain_service.update_item_quantity(
                item=self.domain_service._item_repo.get_by_id(item_id),
                new_quantity=data['quantity']
            )
            
    def remove_item_from_cart(self, user_id: int, item_id: int):
        """ حذف آیتم  """
        logger.info(f"START: Remove Item {item_id} from Cart of User {user_id}")
        try:
            user = get_object_or_404(User, pk=user_id)
            self.domain_service.remove_item(user, item_id)
            logger.info(f"SUCCESS: Item {item_id} removed.")
        except Exception as e:
            logger.error(f"FAILED: Remove Item {item_id}. Error: {str(e)}", exc_info=True)
            raise e

    # ===== متد کمکی (Helper) ===== #
    def _prepare_specs_for_domain(self, product, raw_specs):
        """
        تبدیل داده‌های خام (ID) به آبجکت‌های مورد نیاز دامین سرویس.
        """
        
        prepared = {
            'width': raw_specs.get('width'),
            'height': raw_specs.get('height'),
            'has_design': raw_specs.get('has_design', True),
            'custom_dimensions': raw_specs.get('custom_dimensions')
        }

        # ===== جنس ===== #
        if 'material_id' in raw_specs:
            prepared['material_obj'] = get_object_or_404(
                ProductMaterial, id=raw_specs['material_id'], product=product
            )

        # ===== سایز ===== #
        if 'size_id' in raw_specs:
            prepared['size_obj'] = get_object_or_404(
                ProductSize, id=raw_specs['size_id'], product=product
            )

        # ===== آپشن‌ها ===== #
        if 'option_value_ids' in raw_specs:
            prepared['option_objs'] = list(ProductOptionValue.objects.filter(
                id__in=raw_specs['option_value_ids'],
                product_option__product=product
            ))

        return prepared
    
    def get_all_carts_queryset(self):
        """
        دریافت کوئری‌ست تمام سبدهای خرید برای لیست داشبورد.
        شامل اطلاعات کاربر و خلاصه وضعیت سبد (تعداد آیتم، جمع مبلغ).
        """
        return Cart.objects.select_related('user__customer_profile').prefetch_related(
            'cart_items'
        ).annotate(
            # ===== تعداد آیتم های سبد خرید کاربر ===== #
            items_count=Count('cart_items'),
            # ===== قیمت کل آیتم های سبد خرید کاربر ===== #
            total_amount=Sum(F('cart_items__price'))
        ).order_by('-updated_at')
