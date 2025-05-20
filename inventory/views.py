import io
import os
import requests
import csv
from datetime import timedelta
from django.utils.timezone import localdate
from django.db.models import Sum
from io import BytesIO
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.http import HttpResponse, JsonResponse, FileResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from reportlab.lib.pagesizes import mm
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from django.core.files.temp import NamedTemporaryFile
from core.models import Setting
from .forms import *
from .models import *
from django.core.paginator import Paginator
from django.db.models import Count
from django.db.models.functions import TruncMonth
from web.models import  Reservation
from django.utils import timezone
from django.utils.timezone import now
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.utils import timezone
from datetime import timedelta
from datetime import datetime, timedelta
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
import json
from django.shortcuts import render
from django.utils import timezone
from django.http import JsonResponse


today = timezone.localdate()

# === DASHBOARD ===


@login_required(login_url='/user/login/')
def dashboard(request):
    start_of_today = timezone.make_aware(
        datetime.combine(today, datetime.min.time()))
    end_of_today = timezone.make_aware(datetime.combine(
        today + timedelta(days=1), datetime.min.time()))

    orderTodayCount = OrderItem.objects.filter(
        order_date__range=(start_of_today, end_of_today)).count()
    orderCount = OrderItem.objects.count()
    today_total_amount = OrderItem.objects.filter(order_date__range=(
        start_of_today, end_of_today)).aggregate(total=Sum('total_price'))['total'] or 0
    orders = OrderItem.objects.select_related(
        'menu_item').order_by('-order_date')[:5]

    return render(request, "dashboard.html", {
        "orderTodayCount": orderTodayCount,
        "orderCount": orderCount,
        "orders": orders,
        "today_total_amount": today_total_amount,
    })




def load_menu_items(request):
    search_term = request.GET.get('term', '')  # optional: for search
    menu_items = MenuItem.objects.filter(name__icontains=search_term).values('id', 'name')[:10]
    return JsonResponse(list(menu_items), safe=False)



# DAILY SPECIALS LIST VIEW
class DailySpecialListView(LoginRequiredMixin, ListView):
    model = DailySpecial
    template_name = 'dailyspecials/dailyspecial_list.html'
    context_object_name = 'dailyspecials'


# ORDERS VIEW
@login_required(login_url='/user/login/')
def orders(request):
    orders = OrderItem.objects.all().select_related('table', 'dining_area','order').filter(order_date__gte=now() - timedelta(hours=12)).order_by('-order_date')
    orders_list = OrderItem.objects.all().select_related('table', 'dining_area','order')
    paginator = Paginator(orders_list, 10)
    
    # Get the page number from the request
    page_number = request.GET.get('page')

    # Get the corresponding page
    orders_list = paginator.get_page(page_number)
    return render(request, "order_list.html", {"orders": orders, "orders_list":orders_list})



@login_required(login_url='/user/login/')
def order_transaction_payment(request, order_id):
    order = OrderTransaction.objects.get(id=order_id)
    
    if request.method == 'POST':
        form = OrderTransactionPaymentForm(request.POST, instance=order)
        if form.is_valid():
            # Save the form to the database (this will also save the transaction details)
            form.save()
            return redirect('order_transactions')
    else:
        form = OrderTransactionPaymentForm(instance=order)

    return render(request, 'edit-order-transaction.html', {'form': form, 'order': order})

@login_required(login_url='/user/login/')
def add_order(request):
    today = localdate()
    # unpaid_orders = OrderTransaction.objects.all()
    unpaid_orders = OrderTransaction.objects.filter(created=today, payment_mode="NO PAYMENT").order_by('-id')
    # last_transaction_order = unpaid_orders.first()  # Get the latest unpaid order
   
    menu_items = MenuItem.objects.all().values('id', 'name', 'price') 
    if request.method == 'POST':
        form = OrderTransactionForm(request.POST)
        if form.is_valid():
            order_transaction = form.save(commit=False)
            order_transaction.created_by = request.user
            order_transaction.save()
            return redirect('add_order')  # Ensure 'add_order' is a valid URL name.
    else:
        form = OrderTransactionForm()


    return render(request, 'add_order.html', {
        'form': form,
     
        'all_menu_items': menu_items,
        # 'last_transaction_order': last_transaction_order,
        'unpaid_orders': unpaid_orders,
    })
    
@csrf_exempt
@login_required(login_url='/user/login/')
def submit_orders(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body.decode("utf-8"))
            order_id = data.get("random_id") 
            customer_name = data.get("customer_name")
            order_type = data.get("order_type")
            status = data.get("status")
            special_notes = data.get("special_notes")
            orders = data.get("orders", [])

            if not orders:
                return JsonResponse({"error": "No menu items selected"}, status=400)

            # Fetch the order transaction
            try:
                order_transaction = OrderTransaction.objects.get(random_id=order_id)
            except OrderTransaction.DoesNotExist:
                return JsonResponse({"error": "Order transaction not found"}, status=404)

            # Create multiple order items
            for order in orders:
                try:
                    menu_item = MenuItem.objects.get(id=order["menu_item_id"])
                    OrderItem.objects.create(
                        order=order_transaction,
                        menu_item=menu_item,
                        customer_name=customer_name,
                        quantity=order["quantity"],
                        status=status,
                        special_notes=special_notes,
                        order_type=order_type
                    )
                except MenuItem.DoesNotExist:
                    return JsonResponse({"error": f"Menu item with ID {order['menu_item_id']} not found"}, status=404)

            # Return JSON response with redirect URL
            return JsonResponse({"message": "Orders placed successfully!", "redirect_url": "/manager/orders_transactions/"})

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON format"}, status=400)

    return JsonResponse({"error": "Invalid request method"}, status=405)




# GET SPECIFIC ORDER VIEW
@login_required(login_url="/user/login/")
def getOrder(request, id):
    order = get_object_or_404(OrderItem, id=id) 
    settings = Setting.objects.first()
    return render(request, "getorder.html", {"order": order,  "setting": settings})


# EDIT ORDER VIEW
@login_required(login_url='/user/login/')
def edit_order(request, id):
    order = get_object_or_404(OrderItem, id=id)
    if request.method == 'POST':
        form = OrderForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            return redirect('orders')
    else:
        form = OrderForm(instance=order)
    return render(request, 'edit_order.html', {'form': form})

# DELETE ORDER VIEW
@login_required(login_url='/user/login/')
def delete_order(request, id):
    order = get_object_or_404(OrderItem, id=id)
    if request.method == 'POST':
        order.delete()
        return redirect('orders')
    return render(request, 'delete_order.html', {'order': order})


@login_required(login_url='/user/login/')
def update_order_status(request, order_id):
    # Get the specific order by ID or return 404 if not found
    order = get_object_or_404(OrderItem, id=order_id)

    if request.method == 'POST':
        form = OrderStatusUpdateForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            messages.success(request, f"Order {order.order.id} status updated successfully!")
            return redirect('order_list')  # Redirect to the order list or desired page
    else:
        form = OrderStatusUpdateForm(instance=order)

    return render(request, 'order_status_update.html', {'form': form, 'order': order})

#ORDERTRANSACTIONS

@login_required(login_url="/user/login/")
def orderTransactions(request):

    
    # orders_list = OrderTransaction.objects.all().order_by('-updated', '-id')
   
    orders_list = OrderTransaction.objects.using('default').filter(payment_mode="NO PAYMENT").order_by('-updated', '-id')

    paginator = Paginator(orders_list, 10)
    
    # Get the page number from the request
    page_number = request.GET.get('page')

    # Get the corresponding page
    orders_list = paginator.get_page(page_number)
    return render(request, "ordertransactions.html", {"orders_list":orders_list})
    
#CLEARED ORDERS
@login_required(login_url="/user/login/")
def clearedTransactions(request):
    orders_list = OrderTransaction.objects.filter(payment_mode__in=["CASH", "MOMO PAY", "AIRTEL PAY", "BANK CARD"]).order_by('-id')
    paginator = Paginator(orders_list, 10)
    
    # Get the page number from the request
    page_number = request.GET.get('page')

    # Get the corresponding page
    orders_list = paginator.get_page(page_number)
    return render(request, "cleared_order_transactions.html", {"orders_list":orders_list})

@login_required(login_url="/user/login/")
def getOrderTransaction(request, id):
    order = get_object_or_404(OrderTransaction, id=id)
    settings = Setting.objects.first()
    order_items = OrderItem.objects.filter(order=order)

    # Calculate the correct total by summing item.total_price instead of item.menu_item.price
    total_price = sum(item.total_price for item in order_items)

    context = {
        'order': order,
        'order_items': order_items,
        'total_price': total_price,
        'setting': settings  # Adding settings to context
    }
    return render(request, "getordertransactions.html", context)

# Chart
@login_required(login_url='/user/login/')
def monthly_order_totals(request):
    data = (
        OrderTransaction.objects
        .annotate(month=TruncMonth('created'))
        .values('month')
        .annotate(total_orders=Count('id'))
        .order_by('month')
    )

    # Prepare data for chart
    months = [item['month'].strftime('%b') for item in data]
    totals = [item['total_orders'] for item in data]

    return JsonResponse({'months': months, 'totals': totals})

# Reports
@login_required(login_url='/user/login/')
def pos_reports(requests):
    return render(requests, "reports.html", {})


#birtday reservations
def view_reservations(request):
    reservations = Reservation.objects.all()
    return render(request, 'reservationslists.html', {'reservations':reservations})




#ADMIN
@login_required(login_url='/user/login/')
def category(request):
    form= CategoryForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('dashboard')
    return render(request, 'add_category.html', {'form':form})
    
    
    
def add_menu(request):
    form=MenuForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('dashboard')
    return render(request, 'add_menu.html', {'form':form})

def search_menu_items(request):
    query = request.GET.get("q", "")
    results = MenuItem.objects.filter(name__icontains=query)[:20]
    data = [{"id": item.id, "name": item.name} for item in results]
    return JsonResponse(data, safe=False)



