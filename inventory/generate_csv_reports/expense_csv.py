import csv
from datetime import datetime, timedelta
from django.http import HttpResponse
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from finance.models import Expenses  # adjust import path if needed


@login_required(login_url='/user/login/')
def export_expenses_to_csv(request, time_period='daily'):
    # Map period to filename and heading
    period_map = {
        'daily': ('expenses_today.csv', 'DAILY EXPENSES REPORT'),
        'weekly': ('expenses_this_week.csv', 'WEEKLY EXPENSES REPORT'),
        'monthly': ('expenses_this_month.csv', 'MONTHLY EXPENSES REPORT'),
        'biannual': ('expenses_this_biannual.csv', 'BIANNUAL EXPENSES REPORT'),
        'annual': ('expenses_this_year.csv', 'ANNUAL EXPENSES REPORT')
    }

    filename, heading = period_map.get(
        time_period, ('expenses.csv', 'EXPENSES REPORT'))

    # Calculate date range
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
        return HttpResponse("Invalid time period", status=400)

    # Date range (aware)
    start_of_period = timezone.make_aware(
        datetime.combine(start_date, datetime.min.time()))
    end_of_period = timezone.make_aware(datetime.combine(
        today + timedelta(days=1), datetime.min.time()))

    # Prepare HTTP response
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    writer = csv.writer(response)
    writer.writerow([f' {heading} '])
    writer.writerow([])  # blank line

    # Column headers
    column_headers = [
        ' DATE ', ' CATEGORY ', ' SUPPLIER ',
        ' QUANTITY ', ' UNIT COST ', ' TOTAL AMOUNT ',
        ' AMOUNT PAID ', ' BALANCE ', ' CREATED BY '
    ]
    writer.writerow(column_headers)

    # Query expenses
    expenses = Expenses.objects.select_related('created_by').filter(
        created_date__gte=start_of_period,
        created_date__lt=end_of_period,
        is_active=True
    )

    total_amount = 0
    total_paid = 0
    total_balance = 0
    record_count = 0

    for expense in expenses:
        writer.writerow([
            timezone.localtime(expense.created_date).strftime('%Y-%m-%d'),
            expense.get_category_display() if expense.category else 'N/A',
            expense.name_of_supplier,
            float(expense.quantity),
            float(expense.unit_cost),
            float(expense.total_amount),
            float(expense.amount_paid),
            float(expense.balance),
            expense.created_by.username if expense.created_by else 'Unknown',
        ])
        total_amount += float(expense.total_amount)
        total_paid += float(expense.amount_paid)
        total_balance += float(expense.balance)
        record_count += 1

    # Summary
    writer.writerow([])
    writer.writerow([' SUMMARY '])
    writer.writerow([f'Total Records: {record_count}'])
    writer.writerow([f'Total Amount: Ugx{total_amount:.2f}'])
    writer.writerow([f'Total Paid: Ugx{total_paid:.2f}'])
    writer.writerow([f'Total Balance: Ugx{total_balance:.2f}'])

    return response
