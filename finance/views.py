from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from .forms import RevenueForm, ExpenseForm, AssetForm, LiabilityForm
from django.contrib.auth.decorators import login_required
from datetime import date
from calendar import monthrange
from django.contrib import messages
from django.core.paginator import Paginator
from django.utils import timezone
from finance.models import Asset, Expense, Liability, Revenue
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
    
    expense_query = Expense.objects.filter(
        date__gte=start_date, 
        date__lte=end_date,
        is_active=True
    )
    
    # Calculate totals
    total_revenue = revenue_query.aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
    total_expenses = expense_query.aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
    net_profit = total_revenue - total_expenses
    
    # Get revenue breakdown by category
    revenue_by_category = {}
    for category_code, category_name in Revenue.REVENUE_CHOICES:
        amount = revenue_query.filter(category=category_code).aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
        revenue_by_category[category_name] = amount
    
    # Get expense breakdown by category
    expense_by_category = {}
    for category_code, category_name in Expense.EXPENCE_CHOICES:
        amount = expense_query.filter(category=category_code).aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
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
    Render a comprehensive financial report with income statement, balance sheet,
    and key performance indicators for a selected month and year.
    """
    today = date.today()
    year = int(request.GET.get('year', today.year))
    month = int(request.GET.get('month', today.month))

    # Set the date range for the report
    start_date = date(year, month, 1)
    last_day = monthrange(year, month)[1]
    end_date = date(year, month, last_day)

    # Get financial data
    income = get_income_statement(start_date, end_date)
    balance = get_balance_sheet(end_date)  # Use end of period for balance sheet

    # Calculate key performance indicators
    total_revenue = income.get('total_revenue', Decimal('0.00'))
    total_expenses = income.get('total_expenses', Decimal('0.00'))
    net_profit = income.get('net_profit', Decimal('0.00'))
    
    # Calculate profit margin
    profit_margin = Decimal('0.00')
    if total_revenue > 0:
        profit_margin = (net_profit / total_revenue) * 100
    
    # Calculate debt ratio (liabilities / assets)
    assets = balance.get('assets', Decimal('0.00'))
    liabilities = balance.get('liabilities', Decimal('0.00'))
    debt_ratio = Decimal('0.00')
    if assets > 0:
        debt_ratio = liabilities / assets

    # Check if there's meaningful data to display
    has_data = (
        total_revenue > 0 or 
        total_expenses > 0 or 
        assets > 0 or 
        liabilities > 0
    )

    if not has_data:
        messages.warning(
            request, 
            f"No financial data found for {start_date.strftime('%B %Y')}."
        )

    # Generate context-aware recommendations
    recommendations = []
    
    # Financial health recommendations
    if net_profit < 0:
        recommendations.append(
            "Your business is operating at a loss. Consider reviewing expenses "
            "and identifying cost-cutting opportunities."
        )
        recommendations.append(
            "Explore new revenue streams or marketing strategies to increase sales."
        )
    elif total_expenses > (total_revenue * Decimal('0.7')):
        recommendations.append(
            "Your expenses are high relative to revenue (over 70%). "
            "Analyze your biggest expense categories for potential savings."
        )
    
    # Debt-related recommendations
    if debt_ratio > Decimal('0.6'):
        recommendations.append(
            "Your debt ratio is high. Consider strategies to reduce liabilities "
            "or increase assets to improve financial stability."
        )
    elif debt_ratio < Decimal('0.2') and net_profit > 0:
        recommendations.append(
            "Your debt ratio is low. Consider if strategic investments or financing "
            "could help accelerate business growth."
        )
    
    # General positive recommendation if doing well
    if net_profit > 0 and debt_ratio < Decimal('0.5'):
        recommendations.append(
            "Your business is in good financial health. Consider allocating profits "
            "to emergency reserves or reinvesting in growth opportunities."
        )
    
    # Ensure we have at least one recommendation
    if not recommendations:
        recommendations.append(
            "Continue monitoring your financial metrics and adjust your "
            "business strategy as needed."
        )

    # Prepare RevPAR and ADR if you have the data
    # These are hotel-specific metrics
    revpar = None 
    adr = None  
    

    context = {
        'income': income,
        'balance': balance,
        'profit_margin': profit_margin,
        'debt_ratio': debt_ratio,
        'start_date': start_date,
        'end_date': end_date,
        'recommendations': recommendations,
        'selected_year': year,
        'selected_month': month,
        'revpar': revpar,
        'adr': adr,
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

# @login_required(login_url='/user/login/')
# def revenue(request):
#     revenue_list = Revenue.objects.filter(is_active=True).order_by('-date')
#     paginator = Paginator(revenue_list, 10)
#     page_number = request.GET.get('page')
#     page_obj = paginator.get_page(page_number)
#     return render(request, "revenue.html", {"revenue_list": page_obj})




@login_required(login_url='/user/login/')
def revenue(request):
    # Get selected month and year from query parameters
    selected_month = request.GET.get('month')
    selected_year = request.GET.get('year')

    # Filter by selected month and year if provided
    revenue_list = Revenue.objects.filter(is_active=True).order_by('-date')
    if selected_month and selected_year:
        revenue_list = revenue_list.filter(
            date__year=selected_year,
            date__month=selected_month
        )

    # Calculate total amount
    total_revenue = revenue_list.aggregate(total=Sum('amount'))['total'] or 0

    # Pagination
    paginator = Paginator(revenue_list, 10)
    page_number = request.GET.get('page')
    revenue_page = paginator.get_page(page_number)

    # Pass selected filters and total to the template
    context = {
        "revenue_list": revenue_page,
        "total_revenue": total_revenue,
        "selected_month": selected_month,
        "selected_year": selected_year,
    }
    return render(request, "revenue.html", context)





@login_required(login_url='/user/login/')
def expense(request):
    # Get selected month and year from query parameters
    selected_month = request.GET.get('month')
    selected_year = request.GET.get('year')

    # Filter by selected month and year if provided
    expense_list = Expense.objects.filter(is_active=True).order_by('-date')
    if selected_month and selected_year:
        expense_list = expense_list.filter(
            date__year=selected_year,
            date__month=selected_month
        )

    # Calculate total amount
    total_expense = expense_list.aggregate(total=Sum('amount'))['total'] or 0

    # Pagination
    paginator = Paginator(expense_list, 10)
    page_number = request.GET.get('page')
    expense_page = paginator.get_page(page_number)

    # Pass selected filters and total to the template
    context = {
        "expense_list": expense_page,
        "total_expense": total_expense,
        "selected_month": selected_month,
        "selected_year": selected_year,
    }
    return render(request, "expense.html", context)
