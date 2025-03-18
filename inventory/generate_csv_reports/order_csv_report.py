import csv
from datetime import timedelta, datetime
from django.utils import timezone
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from inventory.models import OrderTransaction, OrderItem

@login_required(login_url='/user/login/')
def export_orders_to_csv(request, time_period='daily'):
    # Define filename based on the time period
    period_filename_map = {
        'daily': 'order_items_today.csv',
        'weekly': 'order_items_this_week.csv',
        'monthly': 'order_items_this_month.csv',
        'biannual': 'order_items_this_biannual.csv',
        'annual': 'order_items_this_year.csv'
    }
    filename = period_filename_map.get(time_period, 'order_items.csv')

    # Determine start and end dates
    end_date = timezone.now().date()

    if time_period == 'daily':
        start_date = end_date
    elif time_period == 'weekly':
        start_date = end_date - timedelta(days=end_date.weekday())  # Monday of the current week
    elif time_period == 'monthly':
        start_date = end_date.replace(day=1)  # First day of the current month
    elif time_period == 'biannual':
        start_date = end_date.replace(month=(end_date.month - 1) // 6 * 6 + 1, day=1)  # First day of the current half-year
    elif time_period == 'annual':
        start_date = end_date.replace(month=1, day=1)  # First day of the current year
    else:
        return HttpResponse("Invalid time period", status=400)

    # Move these lines OUTSIDE the `else` block
    start_of_period = timezone.make_aware(datetime.combine(start_date, datetime.min.time()))
    end_of_period = timezone.make_aware(datetime.combine(end_date + timedelta(days=1), datetime.min.time()))  # End of the period

    # Create HTTP response for CSV
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    # Write CSV header
    writer = csv.writer(response)
    writer.writerow([
        'Order ID', 'Customer Name', 'Mode of Payment', 'Transaction ID', 'Total Price', 'Order Date'
    ])

    # Fetch order transactions where payment_mode is 'Cash', 'Momo', or 'Airtel Pay'
    order_transactions = OrderTransaction.objects.select_related(
        'dining_area', 'table', 'created_by'
    ).filter(
        created__gte=start_of_period, created__lt=end_of_period,
        payment_mode__in=["CASH", "MOMO PAY", "AIRTEL PAY"]  # Filter by specific payment modes
    )
    # Track total sum of total_price
    total_sum = 0

    # Write data rows
    for order in order_transactions:
        order_items = OrderItem.objects.filter(order=order)
        total_price = sum(item.total_price for item in order_items)
        total_sum += total_price  # Add to total sum

        writer.writerow([
            order.random_id,
            order.customer_name,
            order.payment_mode,
            order.transaction_id,
            total_price,  # Use the calculated total price
            order.created.strftime('%Y-%m-%d') if order.created else '',  # Corrected date reference
        ])
    # Write total sum row
    writer.writerow([])
    writer.writerow(['', '', '', 'TOTAL:', total_sum, ''])  # Summed total price

    return response
