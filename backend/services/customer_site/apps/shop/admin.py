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
    ProductAttachment,
    Attachment,   
    ProductOption,
    Option,
    OptionValue,
    ProductPricingConfig,
)

admin.site.register(Product)
admin.site.register(ProductCategory)
admin.site.register(ProductImage)
admin.site.register(ProductSize)
admin.site.register(Size)
admin.site.register(ProductQuantity)
admin.site.register(Quantity)
admin.site.register(ProductAttachment)
admin.site.register(Attachment)
admin.site.register(ProductOption)
admin.site.register(Option)
admin.site.register(OptionValue)
admin.site.register(ProductPricingConfig)
admin.site.register(ProductOptionValue)
