from django.contrib import admin

from core.models import (
    ProductField, ProductFieldChoice, ProductCommentChoices,
    ProductFieldCondition, ProductFormula, Product, FieldDictionary, FieldChoiceDictionary
)

admin.site.register(ProductFormula)
admin.site.register(ProductField)
admin.site.register(FieldDictionary)
admin.site.register(FieldChoiceDictionary)
admin.site.register(ProductFieldCondition)
admin.site.register(ProductFieldChoice)
admin.site.register(Product)
