from django.contrib import admin
from core.models import Transaction, Invoice

# Register your models here.
admin.site.register(Transaction)
admin.site.register(Invoice)