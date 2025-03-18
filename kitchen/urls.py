from django.urls import path
from . import views

urlpatterns = [
    path("", views.kitchen, name='kitchen'),
    path('update_order_status/<int:order_id>/', views.update_order_status, name='update_order_status'),
]