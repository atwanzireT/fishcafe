from django.db import models
from django.db.models import F
from django.db import models
from . import values
from django.db.models import Sum
from django.contrib.auth.models import User

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Supplier(models.Model):
    name = models.CharField(max_length=255)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="suppliers")
    contact_info = models.TextField()
    email = models.EmailField(max_length=255, blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    def get_products(self):
        return self.product_set.all()


class Product(models.Model):
    STOCK_CHOICES = [
        ('in_stock', 'In Stock'),
        ('low', 'Low Stock'),
        ('out', 'Out of Stock'),
    ]

    name = models.CharField(max_length=150, unique=True, verbose_name="Product Name")
    category = models.ForeignKey('Category', on_delete=models.CASCADE, related_name="products", verbose_name="Category")
    stock_status = models.CharField(max_length=20, choices=STOCK_CHOICES, default='in_stock', verbose_name="Stock Status")
    last_updated = models.DateTimeField(auto_now=True, verbose_name="Last Updated")

    class Meta:
        verbose_name = "Product"
        verbose_name_plural = "Products"
        indexes = [
            models.Index(fields=['stock_status']),
        ]
        ordering = ['name']


    def update_stock_status(self):
        """
        Updates the stock status based on the total quantity.
        Avoid calling `save()` here to prevent recursion.
        """
        total_quantity = self.total_quantity()
        if total_quantity == 0:
            new_status = 'out'
        elif total_quantity < 10:  # Customize threshold for low stock
            new_status = 'low'
        else:
            new_status = 'in_stock'

        # Update the stock status only if it has changed
        if self.stock_status != new_status:
            self.stock_status = new_status
            super().save(update_fields=['stock_status'])


    def total_quantity(self):
        """
        Calculates the total quantity of the product from all related batches.
        """
        return self.batches.aggregate(total=Sum('quantity'))['total'] or 0
    
    def total_issued_products(self):
        """
        Calculate the total quantity of issued products for this product.
        """
        return self.issued_items.aggregate(total=Sum('quantity_taken'))['total'] or 0

    
    def get_stock_status_display(self):
        """
        Returns a human-readable stock status for display purposes.
        """
        return dict(self.STOCK_CHOICES).get(self.stock_status, "Unknown")
    
    def quality_remaining(self):
        total_quantity = self.batches.aggregate(total=Sum('quantity'))['total'] or 0
        total_issued = self.issued_items.aggregate(total=Sum('quantity_taken'))['total'] or 0
        return total_quantity - total_issued
    
    def save(self, *args, **kwargs):
 
            # Override save to ensure stock status is updated after the product is saved.
      
        is_new = self.pk is None  # Check if this is a new instance
        super().save(*args, **kwargs)  # Save the instance to get a primary key

        # Update stock status only for existing products with batches
        if not is_new:
            self.update_stock_status()
    

    def __str__(self):
        return self.name


class Batch(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="batches")
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True, blank=True, related_name="batches")
    quantity = models.PositiveIntegerField()
    units = models.CharField(max_length=50, choices=values.unit_choices, blank=True, null=True)
    cost_per_item = models.DecimalField(max_digits=10, decimal_places=2)
    total_cost = models.DecimalField(max_digits=10, decimal_places=2, editable=False)
    expiry_date = models.DateField()
    date_received = models.DateField(auto_now_add=True)

    class Meta:
       ordering = ['-date_received']


    def save(self, *args, **kwargs):
        if hasattr(self, '_saving'):
            return  # Prevent recursive saving
        try:
            self._saving = True
            # Calculate total cost for this batch
            self.total_cost = self.quantity * self.cost_per_item
            super().save(*args, **kwargs)

            # Update the product's stock status only if the product has a primary key
            if self.product_id:
                self.product.update_stock_status()
        finally:
            self._saving = False
    


    def __str__(self):
        return f"Batch {self.id} - {self.product.name} from {self.supplier.name if self.supplier else 'Unknown Supplier'}"


class IssuedProduct(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="issued_items")
    quantity_taken = models.PositiveIntegerField()
    units = models.CharField(max_length=50, choices=values.unit_choices, blank=True, null=True)
    date_taken = models.DateTimeField(auto_now_add=True)
    person_receiving = models.CharField(max_length=100)
    issued_by = models.ForeignKey(User, on_delete=models.CASCADE)
    reason_for_issue = models.TextField(blank=True, null=True)

    def __str__(self):
        return f'{self.quantity_taken} of {self.product.name} issued to {self.person_receiving}'
