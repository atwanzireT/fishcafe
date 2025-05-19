from django.contrib import admin
from .models import Asset, Liability, Expense, Revenue  
@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    list_display = ['name', 'value', 'purchase_date', 'is_active'] 
    search_fields = ['name']
    list_filter = ['is_active', 'purchase_date'] 

@admin.register(Liability)
class LiabilityAdmin(admin.ModelAdmin):
    list_display = ['description', 'amount', 'due_date', 'is_active'] 
    search_fields = ['description']
    list_filter = ['is_active', 'due_date'] 

@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ['category', 'description', 'amount', 'date', 'is_active'] 
    search_fields = ['category', 'description']
    list_filter = ['category', 'is_active', 'date']

@admin.register(Revenue)
class RevenueAdmin(admin.ModelAdmin):
    list_display = ['category', 'description', 'amount', 'received_from', 'date', 'is_active']
    search_fields = ['category', 'received_from', 'description']
    list_filter = ['category', 'is_active', 'date']