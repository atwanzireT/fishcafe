import csv
from django.http import HttpResponse
from django.utils import timezone
from datetime import datetime, time
import pytz

from inventory.models import OrderItem, OrderTransaction


def export_general_order_to_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="general_orders_report.csv"'

    writer = csv.writer(response)

    # CSV Headers
    writer.writerow([
        'Order Date',
        'Order Time',
        'Order ID',
        'Category',
        'Menu Item',
        'Quantity',
        'Unit Price',
        'Total Price',
        'Payment Mode',
        'Served By',
        'Created By',
        'Customer Name',
    ])

    # -------------------------
    # Date handling
    # -------------------------
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    kampala_tz = pytz.timezone('Africa/Kampala')

    if start_date and end_date:
        start_naive = datetime.strptime(start_date, '%Y-%m-%d')
        end_naive = datetime.strptime(end_date, '%Y-%m-%d')

        start_aware = timezone.make_aware(
            datetime.combine(start_naive, time.min), kampala_tz
        )
        end_aware = timezone.make_aware(
            datetime.combine(end_naive, time.max), kampala_tz
        )
    else:
        # fallback: today
        today = timezone.localdate()
        start_aware = timezone.make_aware(
            datetime.combine(today, time.min), kampala_tz
        )
        end_aware = timezone.make_aware(
            datetime.combine(today, time.max), kampala_tz
        )

    # -------------------------
    # Fetch transactions
    # -------------------------
    order_transactions = OrderTransaction.objects.select_related(
        'dining_area', 'table', 'created_by'
    ).filter(
        created__gte=start_aware,
        created__lte=end_aware,
        payment_mode__in=["CASH", "MOMO PAY", "BANK CARD", "AIRTEL PAY"]
    )

    total_sum = 0
    record_count = 0

    # -------------------------
    # Write rows
    # -------------------------
    for order in order_transactions:
        order_items = OrderItem.objects.select_related(
            'menu_item__category'
        ).filter(order=order)

        for item in order_items:
            category_name = (
                item.menu_item.category.name
                if item.menu_item and item.menu_item.category
                else 'N/A'
            )

            order_date_local = timezone.localtime(item.order_date, kampala_tz)

            unit_price = float(item.menu_item.price) if item.menu_item else 0
            total_price = float(item.total_price)

            writer.writerow([
                order_date_local.strftime('%Y-%m-%d'),
                order_date_local.strftime('%H:%M:%S'),
                order.random_id,
                category_name,
                item.menu_item.name if item.menu_item else 'N/A',
                item.quantity,
                unit_price,
                total_price,
                order.payment_mode,
                order.served_by,
                order.created_by.username if order.created_by else 'Unknown',
                order.customer_name,
            ])

            total_sum += total_price
            record_count += 1

    # -------------------------
    # Summary section
    # -------------------------
    writer.writerow([])
    writer.writerow(['SUMMARY'])
    writer.writerow(['Total Records', record_count])
    writer.writerow(['Total Amount (UGX)', f'{total_sum:,.2f}'])

    return response
