from rest_framework import serializers
from .models import OrderTransaction, OrderItem

class OrderTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderTransaction
        fields = ['customer_name', 'special_notes', 'payment_mode']

class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = [
            'order',
            'menu_item',
            'customer_name',
            'dining_area',
            'table',
            'quantity',
            'status',
            'special_notes',
            'order_type',
        ]
