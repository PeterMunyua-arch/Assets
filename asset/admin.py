# admin.py

from django.contrib import admin
from .models import Company, Employee, Asset, InventoryItem, Transaction, AssetAllocation, AssetReturn, Disposal
admin.site.register(Company)
admin.site.register(Employee)
admin.site.register(Asset)
admin.site.register(InventoryItem)
admin.site.register(Transaction)
admin.site.register(AssetAllocation)
admin.site.register(AssetReturn)
admin.site.register(Disposal)
