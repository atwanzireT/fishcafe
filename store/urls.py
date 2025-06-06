from django.urls import path
from . import views
from store.generate_store_reports.product_csv import export_batches_to_csv, export_issued_products_to_csv, export_products_to_csv

urlpatterns = [
    # Home and main views
    path('', views.home, name='storehome'),
    path('tasty/', views.tasty, name='tasty'),

    # Add views
    path('add/new-product/', views.new_product, name='new_product'),
    path('add/category/', views.add_category, name='add_category'),
    path('add/supplier/', views.add_supplier, name='add_supplier'),
    path('product/receive/', views.receive_product, name='receive_product'),
    path('batch/add/', views.add_batch, name='batch_add'),

    # Product management views
    path('product/edit/<int:pk>/', views.edit_product, name='edit_product'),
    path('product/delete/<int:pk>/', views.delete_product, name='delete_product'),

    # List views
    path('suppliers/', views.supplierlist, name='supplier_list'),
    path('products/', views.productlist, name='product_list'),


    # Batch
    path('batch-list/<str:prdID>', views.batches_list, name="batch-list"),

    # Issued Products
    path('issue-product/', views.issued_product_create, name='issue-product'),
    path('view-issued-product/', views.view_issued_product, name='issue-product'),

    # Reports
    # Export Products CSV (default “daily” if no period is given)
    path('export_csv/products/', export_products_to_csv,
         name='export_products_default'),
    path('export_csv/products/<str:time_period>/',
         export_products_to_csv, name='export_products'),

    # Export Batches CSV (default “daily” if no period is given)
    path('export_csv/batches/', export_batches_to_csv,
         name='export_batches_default'),
    path('export_csv/batches/<str:time_period>/',
         export_batches_to_csv, name='export_batches'),

    # Export Issued Products CSV (default “daily” if no period is given)
    path('export_csv/issued-products/', export_issued_products_to_csv,
         name='export_issued_products_default'),
    path('export_csv/issued-products/<str:time_period>/',
         export_issued_products_to_csv, name='export_issued_products'),
]