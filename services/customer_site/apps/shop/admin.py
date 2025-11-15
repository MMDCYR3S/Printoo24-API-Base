from django.contrib import admin

from core.models import (
    Product,
    ProductCategory,
    ProductMaterial,
    ProductImage,
    ProductSize,
    Size,
    Material,
    ProductQuantity,
    Quantity,
    ProductAttachment,
    Attachment,   
    ProductOption,
    Option,
    OptionValue,
)

admin.site.register(Product)
admin.site.register(ProductCategory)
admin.site.register(ProductMaterial)
admin.site.register(ProductImage)
admin.site.register(ProductSize)
admin.site.register(Size)
admin.site.register(Material)
admin.site.register(ProductQuantity)
admin.site.register(Quantity)
admin.site.register(ProductAttachment)
admin.site.register(Attachment)
admin.site.register(ProductOption)
admin.site.register(Option)
admin.site.register(OptionValue)

