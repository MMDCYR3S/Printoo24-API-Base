from django.contrib import admin

from core.models import (
    Product,
    ProductCategory,
    ProductImage,
    ProductSize,
    ProductOption,
    ProductOptionValue,
    Size,
    ProductQuantity,
    Quantity,
    Attachment,   
    ProductOption,
    Option,
    OptionValue,
    ProductPricingConfig,
    ProductCategoryRelation,
)

class ProductImageAdmin(admin.ModelAdmin):
    list_filter = ("product", "user")

admin.site.register(Product)
admin.site.register(ProductCategory)
admin.site.register(ProductImage)
admin.site.register(ProductSize)
admin.site.register(Size)
admin.site.register(ProductQuantity)
admin.site.register(Quantity)
admin.site.register(Attachment)
admin.site.register(ProductOption)
admin.site.register(Option)
admin.site.register(OptionValue)
admin.site.register(ProductPricingConfig)
admin.site.register(ProductOptionValue)
admin.site.register(ProductCategoryRelation)
