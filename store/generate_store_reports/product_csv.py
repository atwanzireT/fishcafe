import csv
from decimal import Decimal
from datetime import datetime, timedelta

from django.http import HttpResponse
from django.utils import timezone
from django.contrib.auth.decorators import login_required

from store.models import Product, Batch, IssuedProduct


# Shared helper to compute start/end datetimes based on time_period
def _get_period_range(time_period):
    today = timezone.localdate()

    if time_period == 'daily':
        start_date = today
    elif time_period == 'weekly':
        start_date = today - timedelta(days=today.weekday())
    elif time_period == 'monthly':
        start_date = today.replace(day=1)
    elif time_period == 'biannual':
        start_date = today.replace(
            month=((today.month - 1) // 6) * 6 + 1, day=1)
    elif time_period == 'annual':
        start_date = today.replace(month=1, day=1)
    else:
        return None, None

    # start at 00:00 of start_date, end at 00:00 of tomorrow (exclusive)
    start_of_period = timezone.make_aware(
        datetime.combine(start_date, datetime.min.time()))
    end_of_period = timezone.make_aware(
        datetime.combine(today + timedelta(days=1), datetime.min.time()))

    return start_of_period, end_of_period


@login_required(login_url='/user/login/')
def export_products_to_csv(request, time_period='daily'):
    """
    Export Products CSV, filtered by last_updated within the given time_period:
    time_period choices: 'daily', 'weekly', 'monthly', 'biannual', 'annual'.
    """
    # Map time_period → (filename, heading)
    period_map = {
        'daily': ('products_today.csv', 'DAILY PRODUCTS REPORT'),
        'weekly': ('products_this_week.csv', 'WEEKLY PRODUCTS REPORT'),
        'monthly': ('products_this_month.csv', 'MONTHLY PRODUCTS REPORT'),
        'biannual': ('products_this_biannual.csv', 'BIANNUAL PRODUCTS REPORT'),
        'annual': ('products_this_year.csv', 'ANNUAL PRODUCTS REPORT'),
    }
    filename, heading = period_map.get(
        time_period, ('products.csv', 'PRODUCTS REPORT'))

    # Compute date range
    start_of_period, end_of_period = _get_period_range(time_period)
    if not start_of_period:
        return HttpResponse("Invalid time period", status=400)

    # Prepare HTTP response
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    writer = csv.writer(response)

    # Heading row
    writer.writerow([heading])
    writer.writerow([])

    # Column headers
    writer.writerow([
        'Product Name',
        'Category',
        'Stock Status',
        'Total Quantity',
        'Total Issued Products',
        'Remaining Quantity',
        'Unit Cost',
        'Total Cost of Remaining Quantity',
        'Last Updated'
    ])

    # Initialize running totals
    grand_total_remaining_qty = 0
    grand_total_remaining_cost = Decimal('0.00')

    # Fetch products with last_updated in range
    products = Product.objects.select_related('category') \
        .prefetch_related('batches') \
        .filter(last_updated__gte=start_of_period,
                last_updated__lt=end_of_period)

    for product in products:
        remaining_qty = product.quality_remaining

        latest_batch = product.batches.first()
        if latest_batch:
            unit_cost = latest_batch.cost_per_item
        else:
            unit_cost = Decimal('0.00')

        total_remaining_cost = Decimal(remaining_qty) * unit_cost

        grand_total_remaining_qty += remaining_qty
        grand_total_remaining_cost += total_remaining_cost

        writer.writerow([
            product.name,
            product.category.name if product.category else 'Uncategorized',
            product.get_stock_status_display(),
            product.total_quantity,
            product.total_issued_products,
            remaining_qty,
            f"{unit_cost:.2f}",
            f"{total_remaining_cost:.2f}",
            product.last_updated.strftime('%Y-%m-%d %H:%M:%S')
        ])

    writer.writerow([])
    writer.writerow([
        'TOTAL',
        '',
        '',
        '',
        '',
        grand_total_remaining_qty,
        '',
        f"{grand_total_remaining_cost:.2f}",
        ''
    ])

    return response


@login_required(login_url='/user/login/')
def export_batches_to_csv(request, time_period='daily'):
    """
    Export Batches CSV, filtered by date_received within the given time_period.
    """
    # Map time_period → (filename, heading)
    period_map = {
        'daily': ('batches_today.csv', 'DAILY BATCHES REPORT'),
        'weekly': ('batches_this_week.csv', 'WEEKLY BATCHES REPORT'),
        'monthly': ('batches_this_month.csv', 'MONTHLY BATCHES REPORT'),
        'biannual': ('batches_this_biannual.csv', 'BIANNUAL BATCHES REPORT'),
        'annual': ('batches_this_year.csv', 'ANNUAL BATCHES REPORT'),
    }
    filename, heading = period_map.get(
        time_period, ('batches.csv', 'BATCHES REPORT'))

    # Compute date range
    start_of_period, end_of_period = _get_period_range(time_period)
    if not start_of_period:
        return HttpResponse("Invalid time period", status=400)

    # Prepare HTTP response
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    writer = csv.writer(response)

    # Heading row
    writer.writerow([heading])
    writer.writerow([])

    # Column headers
    writer.writerow([
        'Batch ID',
        'Product Name',
        'Supplier Name',
        'Quantity',
        'Cost per Item',
        'Total Cost',
        'Expiry Date',
        'Date Received'
    ])

    # Fetch batches with date_received in range
    batches = Batch.objects.select_related('product', 'supplier') \
        .filter(date_received__gte=start_of_period,
                date_received__lt=end_of_period)

    for batch in batches:
        writer.writerow([
            batch.id,
            batch.product.name if batch.product else 'Unknown Product',
            batch.supplier.name if batch.supplier else 'Unknown Supplier',
            batch.quantity,
            f"{batch.cost_per_item:.2f}",
            f"{batch.total_cost:.2f}",
            batch.expiry_date.strftime('%Y-%m-%d'),
            batch.date_received.strftime('%Y-%m-%d'),
        ])

    return response


@login_required(login_url='/user/login/')
def export_issued_products_to_csv(request, time_period='daily'):
    """
    Export Issued Products CSV, filtered by date_taken within the given time_period.
    """
    # Map time_period → (filename, heading)
    period_map = {
        'daily': ('issued_products_today.csv', 'DAILY ISSUED PRODUCTS REPORT'),
        'weekly': ('issued_products_this_week.csv', 'WEEKLY ISSUED PRODUCTS REPORT'),
        'monthly': ('issued_products_this_month.csv', 'MONTHLY ISSUED PRODUCTS REPORT'),
        'biannual': ('issued_products_this_biannual.csv', 'BIANNUAL ISSUED PRODUCTS REPORT'),
        'annual': ('issued_products_this_year.csv', 'ANNUAL ISSUED PRODUCTS REPORT'),
    }
    filename, heading = period_map.get(
        time_period, ('issued_products.csv', 'ISSUED PRODUCTS REPORT'))

    # Compute date range
    start_of_period, end_of_period = _get_period_range(time_period)
    if not start_of_period:
        return HttpResponse("Invalid time period", status=400)

    # Prepare HTTP response
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    writer = csv.writer(response)

    # Heading row
    writer.writerow([heading])
    writer.writerow([])

    # Column headers
    writer.writerow([
        'Product Name',
        'Quantity Taken',
        'Units',
        'Date Taken',
        'Person Receiving',
        'Issued By',
        'Reason for Issue'
    ])

    # Fetch issued products with date_taken in range
    issued_products = IssuedProduct.objects.select_related('product', 'issued_by') \
        .filter(date_taken__gte=start_of_period,
                date_taken__lt=end_of_period)

    for ip in issued_products:
        writer.writerow([
            ip.product.name,
            ip.quantity_taken,
            ip.units,
            ip.date_taken.strftime('%Y-%m-%d'),
            ip.person_receiving,
            ip.issued_by.username,
            ip.reason_for_issue
        ])

    return response
