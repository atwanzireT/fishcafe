from django.contrib import admin
from .models import (
    Category, MenuItem, DiningArea, Table, OrderTransaction, OrderItem, 
)

# Register models with custom admin classes
@admin.register(OrderTransaction)
class OrderTransactionAdmin(admin.ModelAdmin):
    list_display = ['random_id', 'customer_name', 'payment_mode', 'created_by', 'created']
    search_fields = ['random_id', 'customer_name']

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'grouping', 'description']
    search_fields = ['name', 'grouping']

@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'is_available']
    list_filter = ['category', 'is_available']
    search_fields = ['name', 'description']

@admin.register(DiningArea)
class DiningAreaAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']
    search_fields = ['name']

@admin.register(Table)
class TableAdmin(admin.ModelAdmin):
    list_display = ['table_number', 'dining_area', 'capacity', 'is_available']
    list_filter = ['dining_area', 'is_available']

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):  # Renamed to match the model
    list_display = ['customer_name', 'menu_item', 'order_date', 'status', 'order_type', 'total_price']
    list_filter = ['order_date', 'status', 'order_type']
    search_fields = ['random_id', 'customer_name', 'special_notes']





