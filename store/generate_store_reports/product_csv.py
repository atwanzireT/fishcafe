import csv
from django.http import HttpResponse
from store.models import Product, Batch, IssuedProduct

def export_products_to_csv(request):
    # Set up the HTTP response with the appropriate CSV header
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="products.csv"'

    # Create a CSV writer
    writer = csv.writer(response)

    # Write the header row
    writer.writerow([
        'Product Name', 'Category', 'Stock Status', 'Total Quantity',
        'Total Issued Products', 'Remaining Quantity'
    ])

    # Write data rows for each product
    products = Product.objects.select_related('category').all()
    for product in products:
        writer.writerow([
            product.name,
            product.category.name if product.category else 'Uncategorized',
            product.get_stock_status_display(),
            product.total_quantity(),
            product.total_issued_products(),
            product.quality_remaining()
        ])

    return response

def export_batches_to_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="batches.csv"'

    writer = csv.writer(response)

    writer.writerow([
        'Batch ID', 'Product Name', 'Supplier Name', 'Quantity', 'Cost per Item',
        'Total Cost', 'Expiry Date', 'Date Received'
    ])

    batches = Batch.objects.select_related('product', 'supplier').all()
    for batch in batches:
        writer.writerow([
            batch.id,
            batch.product.name if batch.product else 'Unknown Product',
            batch.supplier.name if batch.supplier else 'Unknown Supplier',
            batch.quantity,
            batch.cost_per_item,
            batch.total_cost,
            batch.expiry_date,
            batch.date_received
        ])

    return response

def export_issued_products_to_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="issued_products.csv"'

    writer = csv.writer(response)

    writer.writerow([
        'Product Name', 'Quantity Taken', 'Units', 'Date Taken',
        'Person Receiving', 'Issued By', 'Reason for Issue'
    ])

    issued_products = IssuedProduct.objects.select_related('product', 'issued_by').all()
    for issued_product in issued_products:
        writer.writerow([
            issued_product.product.name,
            issued_product.quantity_taken,
            issued_product.units,
            issued_product.date_taken,
            issued_product.person_receiving,
            issued_product.issued_by.username,
            issued_product.reason_for_issue
        ])

    return response
