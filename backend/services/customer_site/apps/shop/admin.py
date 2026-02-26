from django.contrib import admin

from core.models import (
    ProductField, ProductFieldChoice, ProductCommentChoices,
    ProductFieldCondition, ProductFormula
)

admin.site.register(ProductFormula)
admin.site.register(ProductField)
admin.site.register(ProductFieldCondition)
admin.site.register(ProductFieldChoice)
