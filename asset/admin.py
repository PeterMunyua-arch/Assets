# admin.py



from django.contrib import admin
from .models import Company, Employee, Asset, InventoryItem, Transaction, AssetAllocation, AssetReturn, Damaged

class AssetAdmin(admin.ModelAdmin):
    search_fields = ['serial_number', 'name', 'type']  # Add the fields you want to search by

class EmployeeAdmin(admin.ModelAdmin):
    search_fields = ['first_name', 'last_name', 'email']  # Add the fields you want to search by

class AssetAllocationAdmin(admin.ModelAdmin):
    search_fields = ['asset__serial_number', 'employee_allocated__first_name', 'employee_allocated__last_name']  # Add the fields you want to search by

admin.site.register(Asset, AssetAdmin)
admin.site.register(Employee, EmployeeAdmin)
admin.site.register(AssetAllocation, AssetAllocationAdmin)
admin.site.register(Company)
admin.site.register(InventoryItem)
admin.site.register(Transaction)
admin.site.register(AssetReturn)
admin.site.register(Damaged)
