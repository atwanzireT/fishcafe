from django.urls import path
from . import api_views as views

urlpatterns = [
    # OrderTransaction URLs
    path('ordertransactions/', views.OrderTransactionListView.as_view(), name='ordertransaction-list'),
    # List all order transactions
    path('ordertransactions/create/', views.OrderTransactionCreateView.as_view(), name='ordertransaction-create'),
    # Create an order transaction
    path('ordertransactions/<int:pk>/', views.OrderTransactionRetrieveView.as_view(), name='ordertransaction-detail'),
    # Retrieve a specific order transaction
    path('ordertransactions/<int:pk>/update/', views.OrderTransactionUpdateView.as_view(),
         name='ordertransaction-update'),  # Update an order transaction
    path('ordertransactions/<int:pk>/destroy/', views.OrderTransactionDestroyView.as_view(),
         name='ordertransaction-destroy'),  # Delete an order transaction

    # OrderItem URLs
    path('orderitems/', views.OrderItemListView.as_view(), name='orderitem-list'),  # List all order items
    path('orderitems/create/', views.OrderItemCreateView.as_view(), name='orderitem-create'),  # Create an order item
    path('orderitems/<int:pk>/', views.OrderItemRetrieveView.as_view(), name='orderitem-detail'),
    # Retrieve a specific order item
    path('orderitems/<int:pk>/update/', views.OrderItemUpdateView.as_view(), name='orderitem-update'),
    # Update an order item
    path('orderitems/<int:pk>/destroy/', views.OrderItemDestroyView.as_view(), name='orderitem-destroy'),
    # Delete an order item
]
