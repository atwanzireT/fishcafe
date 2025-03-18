import csv
from django.http import HttpResponse
from inventory.models import OrderItem


def  export_paid_order_to_csv(request):
    # Create the HttpResponse object with content type for CSV
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="order_items_report.csv"'

    # Create a CSV writer object
    writer = csv.writer(response)

    # Write the headers to the CSV file
    writer.writerow([
        'Order ID', 'Menu Item', 'Customer Name', 'Table', 'Dining Area', 'Quantity', 
        'Total Price', 'Status', 'Order Type', 'Special Notes','Mode of Payment', 'Transaction ID', 'Order Date'
    ])

    # Fetch all OrderItem records (you can add filters if needed)
    order_items = OrderItem.objects.exclude(order__payment_mode ="NO PAYMENT").select_related('menu_item', 'order', 'table', 'dining_area')

    # Write the data rows
    for item in order_items:
        writer.writerow([
            item.order.random_id,
            item.menu_item.name if item.menu_item else 'N/A',
            item.customer_name,
            item.table.table_number if item.table else 'N/A',
            item.dining_area.name if item.dining_area else 'N/A', 
            item.quantity,
            item.total_price,
            item.status, 
            item.order_type, 
            item.special_notes if item.special_notes else 'N/A',
            item.order.payment_mode,
            item.order.transaction_id,
            item.order_date.strftime('%Y-%m-%d'), 
        ])

    return response
