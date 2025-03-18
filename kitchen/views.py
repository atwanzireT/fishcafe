from django.shortcuts import render
from inventory.models import *
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.views.decorators.http import require_POST
from datetime import date
from django.core.paginator import Paginator

def kitchen(request):
    """
    Displays all order items for the kitchen view.
    """
    orders = OrderItem.objects.all()
    paginator = Paginator(orders, 5)
    page_number = request.GET.get('page')
    orders = paginator.get_page(page_number)
    return render(request, "kitchen.html", {"orders": orders})

@require_POST
def update_order_status(request, order_id):
    """
    Updates the status of a specific order item.
    """
    order = get_object_or_404(OrderItem, id=order_id)
    new_status = request.POST.get('status')
    
    # Validate the status to match available choices in the model
    valid_statuses = dict(OrderItem._meta.get_field('status').choices)
    if new_status in valid_statuses:
        order.status = new_status
        order.save()
        messages.success(request, f"Order {order.id} status updated to {new_status}.")
    else:
        messages.error(request, "Invalid status selected.")
    
    return redirect('kitchen')