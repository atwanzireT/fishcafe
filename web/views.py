from django.shortcuts import render, redirect
from inventory.models import Category, MenuItem 
from .models import Reservation
from .forms import ReservationForm
from django.contrib import messages


def make_reservation(request):
    if request.method == 'POST':
        form = ReservationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your reservation has been successfully submitted!')
            return redirect('reservation_success')  # Redirect to the success page
    else:
        form = ReservationForm()
    return render(request, 'reservation.html', {'form': form})

def reservation_success(request):

    return render(request, 'reservation_success.html')


# Create your views here.
def home(request):
    dishes = Category.objects.order_by('?')[:12]
    foods = MenuItem.objects.order_by('?')[:10]
    return render(request, "index.html", {"dishes": dishes, "foods": foods})


def menu(request):
    menu = MenuItem.objects.all()
    return render(request, "menu.html", {"menu": menu})

def food_filter(request, id):
    food_item = MenuItem.objects.filter(category = id)
    food_category = Category.objects.get(id = id)
    return render(request, "foods_filter.html", {"food_item":food_item, "category":food_category})