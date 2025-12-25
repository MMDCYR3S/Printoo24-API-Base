from django.contrib import admin

from core.models import User, Role, UserRole, CustomerProfile, Address, City, Province
from .models import Wallet, WalletTransaction
admin.site.register(User)
admin.site.register(Role)
admin.site.register(UserRole)
admin.site.register(CustomerProfile)
admin.site.register(Wallet)
admin.site.register(WalletTransaction)
admin.site.register(Address)
admin.site.register(City)
admin.site.register(Province)
