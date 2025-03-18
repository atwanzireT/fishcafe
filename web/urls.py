from django.urls import path
from . import views
from .views import *
from django.contrib.auth import views as auth_views

urlpatterns = [
    path("", views.home, name="home"),
    path("menu/", views.menu, name="menu"),
    path("foods/<str:id>", views.food_filter, name="menu"),
    path("make_reservation", views.make_reservation, name='make_reservation'),
    path('reservation-success/', views.reservation_success, name='reservation_success'),
]