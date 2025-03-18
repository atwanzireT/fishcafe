from rest_framework import generics, permissions
from .models import OrderTransaction, OrderItem
from .serializers import OrderTransactionSerializer, OrderItemSerializer

# OrderTransaction List View
class OrderTransactionListView(generics.ListAPIView):
    queryset = OrderTransaction.objects.all()
    serializer_class = OrderTransactionSerializer
    permission_classes = [permissions.IsAuthenticated]

# OrderTransaction Create View
class OrderTransactionCreateView(generics.CreateAPIView):
    queryset = OrderTransaction.objects.all()
    serializer_class = OrderTransactionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


# OrderTransaction Retrieve View
class OrderTransactionRetrieveView(generics.RetrieveAPIView):
    queryset = OrderTransaction.objects.all()
    serializer_class = OrderTransactionSerializer
    permission_classes = [permissions.IsAuthenticated]


# OrderTransaction Update View
class OrderTransactionUpdateView(generics.UpdateAPIView):
    queryset = OrderTransaction.objects.all()
    serializer_class = OrderTransactionSerializer
    permission_classes = [permissions.IsAuthenticated]


# OrderTransaction Destroy View
class OrderTransactionDestroyView(generics.DestroyAPIView):
    queryset = OrderTransaction.objects.all()
    serializer_class = OrderTransactionSerializer
    permission_classes = [permissions.IsAuthenticated]


# OrderItem List View
class OrderItemListView(generics.ListAPIView):
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer
    permission_classes = [permissions.IsAuthenticated]

# OrderItem Create View
class OrderItemCreateView(generics.CreateAPIView):
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer
    permission_classes = [permissions.IsAuthenticated]


# OrderItem Retrieve View
class OrderItemRetrieveView(generics.RetrieveAPIView):
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer
    permission_classes = [permissions.IsAuthenticated]


# OrderItem Update View
class OrderItemUpdateView(generics.UpdateAPIView):
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer
    permission_classes = [permissions.IsAuthenticated]


# OrderItem Destroy View
class OrderItemDestroyView(generics.DestroyAPIView):
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer
    permission_classes = [permissions.IsAuthenticated]
