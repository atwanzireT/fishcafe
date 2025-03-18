from django.contrib import admin
from .models import Category, Supplier, Product, IssuedProduct, Batch

# Register your models here.
admin.site.register(Batch)
admin.site.register(Category)
admin.site.register(Supplier)
admin.site.register(Product)
admin.site.register(IssuedProduct)
