from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from .forms import RevenueForm, ExpenseForm, AssetForm, LiabilityForm
from django.contrib.auth.decorators import login_required
from datetime import date, datetime, timedelta
from calendar import monthrange
from django.contrib import messages
from django.core.paginator import Paginator
from django.utils import timezone
from finance.models import Asset, Expenses, Liability, Revenue
from django.db.models import Sum

from inventory.models import *
from datetime import date


# Financial Documents
def get_income_statement(start_date, end_date, user=None):
    """
    Calculate income statement data for the given date range.
    
    Args:
        start_date (date): Starting date for the period
        end_date (date): Ending date for the period
        user (User, optional): User object for filtering data (if needed)
    
    Returns:
        dict: Income statement data including total_revenue, total_expenses, and net_profit
    """
    # Filter revenue and expenses for the date range
    revenue_query = Revenue.objects.filter(
        date__gte=start_date, 
        date__lte=end_date,
        is_active=True
    )
    
    expense_query = Expenses.objects.filter(
        created_date__gte=start_date,
        created_date__lte=end_date,
        is_active=True
    )
    
    # Calculate totals
    total_revenue = revenue_query.aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
    total_expenses = expense_query.aggregate(Sum('amount_paid'))[
        'amount_paid__sum'] or Decimal('0.00')
    net_profit = total_revenue - total_expenses
    
    # Get revenue breakdown by category
    revenue_by_category = {}
    for category_code, category_name in Revenue.REVENUE_CHOICES:
        amount = revenue_query.filter(category=category_code).aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
        revenue_by_category[category_name] = amount
    
    # Get expense breakdown by category
    expense_by_category = {}
    for category_code, category_name in Expenses. EXPENSE_CHOICES:
        amount = expense_query.filter(category=category_code).aggregate(Sum('amount_paid'))['amount_paid__sum'] or Decimal('0.00')
        expense_by_category[category_name] = amount
    
    return {
        'total_revenue': total_revenue,
        'total_expenses': total_expenses,
        'net_profit': net_profit,
        'revenue_by_category': revenue_by_category,
        'expense_by_category': expense_by_category
    }

def get_balance_sheet(as_of_date=None):
    """
    Calculate balance sheet data as of a specific date.
    
    Args:
        as_of_date (date, optional): Date to calculate balance sheet for. Defaults to today.
    
    Returns:
        dict: Balance sheet data including assets, liabilities, and equity
    """
    if as_of_date is None:
        as_of_date = date.today()
    
    # Get active assets and calculate depreciation
    assets_query = Asset.objects.filter(is_active=True)
    
    total_assets_value = assets_query.aggregate(Sum('value'))['value__sum'] or Decimal('0.00')
    
    # Calculate depreciation
    total_depreciation = sum(
        asset.depreciation_amount for asset in assets_query
        if asset.purchase_date and asset.purchase_date <= as_of_date
    )
    
    # Get active liabilities
    liabilities_query = Liability.objects.filter(is_active=True)
    if as_of_date:
        # Only include liabilities that existed on or before the as_of_date
        liabilities_query = liabilities_query.filter(due_date__lte=as_of_date)
    
    total_liabilities = liabilities_query.aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
    
    # Asset value minus depreciation
    asset_value = total_assets_value - Decimal(str(total_depreciation))
    
    # Calculate equity (Assets - Liabilities)
    equity = asset_value - total_liabilities
    
    return {
        'assets': asset_value,
        'liabilities': total_liabilities,
        'equity': equity
    }


@login_required(login_url='/user/login/')
def financial_report(request):
    """
    Render a financial report for a custom date range or default to the current month.
    """
    # Get date inputs from query params
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')

    today = date.today()

    try:
        start_date = datetime.strptime(
            start_date_str, "%Y-%m-%d").date() if start_date_str else date(today.year, today.month, 1)
        end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date() if end_date_str else date(
            today.year, today.month, monthrange(today.year, today.month)[1])
    except ValueError:
        messages.error(request, "Invalid date format. Please use YYYY-MM-DD.")
        start_date = date(today.year, today.month, 1)
        end_date = date(today.year, today.month,
                        monthrange(today.year, today.month)[1])

    # Get financial data
    income = get_income_statement(start_date, end_date)
    balance = get_balance_sheet(end_date)

    total_revenue = income.get('total_revenue', Decimal('0.00'))
    total_expenses = income.get('total_expenses', Decimal('0.00'))
    net_profit = income.get('net_profit', Decimal('0.00'))

    profit_margin = (net_profit / total_revenue) * \
        100 if total_revenue > 0 else Decimal('0.00')
    assets = balance.get('assets', Decimal('0.00'))
    liabilities = balance.get('liabilities', Decimal('0.00'))
    debt_ratio = (liabilities / assets) if assets > 0 else Decimal('0.00')

    has_data = total_revenue > 0 or total_expenses > 0 or assets > 0 or liabilities > 0
    if not has_data:
        messages.warning(
            request, f"No financial data found for the selected period ({start_date} to {end_date}).")

    # Recommendations
    recommendations = []

    if net_profit < 0:
        recommendations += [
            "Your business is operating at a loss. Consider reviewing expenses.",
            "Explore new revenue streams to increase income."
        ]
    elif total_expenses > (total_revenue * Decimal('0.7')):
        recommendations.append(
            "Expenses exceed 70% of revenue. Review your major cost centers.")

    if debt_ratio > Decimal('0.6'):
        recommendations.append(
            "High debt ratio. Consider reducing liabilities.")
    elif debt_ratio < Decimal('0.2') and net_profit > 0:
        recommendations.append(
            "Low debt ratio. You may explore growth through strategic investments.")

    if net_profit > 0 and debt_ratio < Decimal('0.5'):
        recommendations.append(
            "Strong financial health. Consider reinvesting profits.")

    if not recommendations:
        recommendations.append(
            "Continue monitoring and adjusting your strategy.")

    context = {
        'income': income,
        'balance': balance,
        'profit_margin': profit_margin,
        'debt_ratio': debt_ratio,
        'start_date': start_date,
        'end_date': end_date,
        'recommendations': recommendations,
        'revpar': None,
        'adr': None,
        'has_data': has_data
    }

    return render(request, 'financial_summary.html', context)



@login_required(login_url='/user/login/')
def add_revenue(request):
    form = RevenueForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        revenue = form.save(commit=False)
        revenue.created_by = request.user
        revenue.updated_by = request.user
        revenue.save()
        messages.success(request, "Revenue record added successfully.")
        return redirect('revenue')
    return render(request, 'add_revenue.html', {'form': form})

@login_required(login_url='/user/login/')
def add_expense(request):
    form = ExpenseForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        expense = form.save(commit=False)
        expense.created_by = request.user
        expense.updated_by = request.user
        expense.save()
        messages.success(request, "Expense record added successfully.")
        return redirect('expense')
    return render(request, 'add_expense.html', {'form': form})

@login_required(login_url='/user/login/')
def add_asset(request):
    form = AssetForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        asset = form.save(commit=False)
        asset.created_by = request.user
        asset.updated_by = request.user
        asset.save()
        messages.success(request, "Asset record added successfully.")
        return redirect('assets')
    return render(request, 'add_asset.html', {'form': form})

@login_required(login_url='/user/login/')
def add_liability(request):
    form = LiabilityForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        liability = form.save(commit=False)
        liability.created_by = request.user
        liability.updated_by = request.user
        liability.save()
        messages.success(request, "Liability record added successfully.")
        return redirect('liabilities')
    return render(request, 'add_liability.html', {'form': form})

@login_required(login_url='/user/login/')
def all_assets(request):
    assets_list = Asset.objects.filter(is_active=True).order_by('-purchase_date')
    paginator = Paginator(assets_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, "assets.html", {"assets_list": page_obj})

@login_required(login_url='/user/login/')
def liabities(request):
    all_liability = Liability.objects.filter(is_active=True).order_by('-due_date')
    paginator = Paginator(all_liability, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, "liability.html", {"all_liability": page_obj})



@login_required(login_url='/user/login/')
def revenue(request):
    # Get date range from query params
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    revenue_list = Revenue.objects.filter(is_active=True).order_by('-date')

    # Filter by date range if provided
    if start_date and end_date:
        try:
            start = datetime.strptime(start_date, "%Y-%m-%d").date()
            end = datetime.strptime(end_date, "%Y-%m-%d").date()
            revenue_list = revenue_list.filter(date__range=(start, end))
        except ValueError:
            pass  # Handle invalid date input silently

    # Calculate total amount
    total_revenue = revenue_list.aggregate(total=Sum('amount'))['total'] or 0

    # Pagination
    paginator = Paginator(revenue_list, 10)
    page_number = request.GET.get('page')
    revenue_page = paginator.get_page(page_number)

    context = {
        "revenue_list": revenue_page,
        "total_revenue": total_revenue,
        "start_date": start_date,
        "end_date": end_date,
    }
    return render(request, "revenue.html", context)


@login_required(login_url='/user/login/')
def expense(request):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    expense_list = Expenses.objects.filter(
        is_active=True).order_by('-created_date')

    if start_date and end_date:
        try:
            start = datetime.strptime(start_date, "%Y-%m-%d")
            # include full end date
            end = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1)
            expense_list = expense_list.filter(
                created_date__gte=start,
                created_date__lt=end
            )
        except ValueError:
            pass  # Invalid dates will be ignored

    total_expense = expense_list.aggregate(
        total=Sum('amount_paid'))['total'] or 0

    paginator = Paginator(expense_list, 10)
    page_number = request.GET.get('page')
    expense_page = paginator.get_page(page_number)

    context = {
        "expense_list": expense_page,
        "total_expense": total_expense,
        "start_date": start_date,
        "end_date": end_date,
    }
    return render(request, "expense.html", context)
