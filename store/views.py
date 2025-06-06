from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from django.db.models import Sum, F, FloatField
from .forms import CategoryForm, SupplierForm, ProductForm, IssuedProductForm, BatchForm
from .models import Category, Supplier, Product, IssuedProduct, Batch
from django.core.paginator import Paginator

# Static Pages
def tasty(request):
    return render(request, 'daze.html')


@login_required(login_url='/user/login/')
def home(request):
    # 1) Fetch all products (latest first) and paginate
    product_list = Product.objects.all().order_by('-id')
    paginator = Paginator(product_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # 2) For each product on this page, pull the latest batch’s unit cost,
    #    then compute remaining_total_cost = quality_remaining × unit_cost.
    for product in page_obj:
        # because Batch.Meta.ordering = ['-date_received']
        latest_batch = product.batches.first()
        if latest_batch:
            unit_cost = latest_batch.cost_per_item
        else:
            unit_cost = 0  # or Decimal('0.00') if you prefer

        # quality_remaining is already a number (int or Decimal), not a method:
        remaining_qty = product.quality_remaining

        # Multiply to get the cost of whatever is left:
        remaining_total_cost = remaining_qty * unit_cost

        # Attach these values so the template can read them directly:
        product.unit_cost = unit_cost
        product.remaining_total_cost = remaining_total_cost

    return render(request, 'storehome.html', {"products": page_obj})

# Add Views
@login_required(login_url='/user/login/')
def new_product(request):
    form = ProductForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('product_list')
    return render(request, 'store/add_new_product.html', {'form': form})

@login_required(login_url='/user/login/')
def suppliers(request):
    suppliers = Supplier.objects.all()
    return render(request, 'list/supplierlist.html', {'suppfliers': suppliers})


@login_required(login_url='/user/login/')
def add_supplier(request):
    form = SupplierForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('supplier_list')
    return render(request, 'store/add_suppiler.html', {'form': form})

@login_required(login_url='/user/login/')
def add_category(request):
    form = CategoryForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, "Product category added successfully")
        return redirect('product_list')
    return render(request, 'store/add_category.html', {'form': form})

@login_required(login_url='/user/login/')
def receive_product(request):
    form = ProductForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, "Product received successfully")
        return redirect('product_list')
    return render(request, 'store/add_product.html', {'form': form})

# Edit and Delete Views
@login_required(login_url='/user/login/')
def edit_product(request, pk):
    product = get_object_or_404(Batch, pk=pk)
    form = BatchForm(request.POST or None, instance=product)
    if form.is_valid():
        form.save()
        messages.success(request, "Product updated successfully.")
        return redirect('storehome')
    return render(request, 'store/edit.html', {'form': form, 'product': product})

@login_required(login_url='/user/login/')
def delete_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.delete()
        messages.success(request, "Product deleted successfully.")
        return redirect('productlist')
    return render(request, 'store/delete.html', {'product': product})

# List Views
@login_required(login_url='/user/login/')
def supplierlist(request):
    suppliers = Supplier.objects.all()
    return render(request, 'lists/supplierlist.html', {'suppliers': suppliers})

@login_required(login_url='/user/login/')
def productlist(request):
    products = Product.objects.all()
    return render(request, 'lists/productlist.html', {'products': products})

@login_required(login_url='/user/login/')
def issued_product_list(request):
    issued_products = IssuedProduct.objects.all()
    return render(request, 'lists/issued_product_list.html', {'issued_products': issued_products})


# Batches
@login_required(login_url='/user/login/')
def add_batch(request):
    if request.method == 'POST':
        form = BatchForm(request.POST)
        if form.is_valid():
            form.save() 
            return redirect(reverse('storehome'))
    else:
        form = BatchForm()
    
    return render(request, 'batch_form.html', {'form': form})

@login_required(login_url='/user/login/') 
def batches_list(request, prdID): 
    batches = Batch.objects.filter(product__id=prdID) 
    context = {"batches": batches} 
    return render(request, "lists/batcheslist.html", context)


def issued_product_create(request):
    if request.method == 'POST':
        form = IssuedProductForm(request.POST)
        if form.is_valid():
            store = form.save(commit=False)
            store.issued_by = request.user
            store.save() 
            return redirect('storehome') 
    else:
        form = IssuedProductForm()
    return render(request, 'store/issued_product_form.html', {'form': form})

def view_issued_product(request):
    issued_products = IssuedProduct.objects.all().order_by('-date_taken')  # Add ordering for better display
    paginator = Paginator(issued_products, 10)  # Show 10 items per page

    page_number = request.GET.get('page')  # Get the current page number from the request
    issued_products = paginator.get_page(page_number)  # Get the products for the current page

    return render(request, "issued_products.html", {"issued_products": issued_products})