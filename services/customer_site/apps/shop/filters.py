# customer_site/shop/filters.py

import django_filters
from core.models import Product, ProductCategory, Size, Material, OptionValue

class ProductFilter(django_filters.FilterSet):
    """
    کلاس فیلتر پیشرفته برای محصولات.
    این کلاس به ما اجازه می‌دهد بر اساس فیلدهای مستقیم محصول و همچنین
    ویژگی‌های مرتبط با آن (مانند سایز، جنس و آپشن) فیلتر کنیم.
    """
    # ===== فیلتر براساس نام محصول ===== #
    name = django_filters.CharFilter(field_name='name', lookup_expr='icontains')
    
    # ===== فیلتر براساس دسته بندی ===== #
    category = django_filters.ModelChoiceFilter(
        field_name='category__slug',
        to_field_name='slug',
        queryset=ProductCategory.objects.all()
    )
    
    # ===== فیلتر براساس سایز ===== #
    sizes = django_filters.ModelMultipleChoiceFilter(
        field_name='productsize__size__id',
        to_field_name='id',
        queryset=Size.objects.all()
    )

    # ====== فیلتر براساس material ===== #
    materials = django_filters.ModelMultipleChoiceFilter(
        field_name='productmaterial__material__id',
        to_field_name='id',
        queryset=Material.objects.all()
    )
    
    # ====== فیلتر براساس ویژگی های منحصر به فرد محصول ===== #
    options = django_filters.ModelMultipleChoiceFilter(
        field_name='productoption__option_value__id',
        to_field_name='id',
        queryset=OptionValue.objects.all()
    )

    class Meta:
        model = Product
        fields = ['name', 'category', 'sizes', 'materials', 'options']
