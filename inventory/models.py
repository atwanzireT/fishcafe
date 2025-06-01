from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now
import uuid
import random
import string
from decimal import Decimal, InvalidOperation

def generate_random_id():
    return str(random.randint(100000, 999999))

class Category(models.Model):
    GROUPING_CHOICES = (
        ("Starter", "Starter"),
        ("Main Dishes", "Main Dishes"),
        ("Desserts & Beverages", "Desserts & Beverages"),
    )
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=100)
    image_url = models.ImageField(blank=True, null=True, upload_to="category_items")
    grouping = models.CharField(max_length=100, choices=GROUPING_CHOICES)

    def __str__(self):
        
        return self.name

class MenuItem(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="menu_items")
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    is_available = models.BooleanField(default=True)
    image_url = models.ImageField(blank=True, null=True, upload_to="menu_items")

    def __str__(self):
        return self.name

class DailySpecial(models.Model):
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    description = models.TextField()

    def __str__(self):
        return self.menu_item.name

class DiningArea(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

class Table(models.Model):
    table_number = models.IntegerField()
    dining_area = models.ForeignKey(DiningArea, on_delete=models.CASCADE, related_name='tables')
    capacity = models.IntegerField()  # Number of seats at the table
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return f"Table {self.table_number} in {self.dining_area.name}"

class OrderTransaction(models.Model):
    pay_mode = (
        ("NO PAYMENT", "NO PAYMENT"),
        ("CASH", "CASH"),
        ("MOMO PAY", "MOMO PAY"),
        ("AIRTEL PAY", "AIRTEL PAY"),
        ("BANK CARD", "BANK CARD"),
    )
    random_id = models.CharField(max_length=6, unique=True, editable=False, default=generate_random_id)
    customer_name = models.CharField(max_length=255, blank=True, null=True, default="FishPoint Customer")
    served_by = models.CharField(
        max_length=255, blank=True, null=True, default="Waitress")
    dining_area = models.ForeignKey(DiningArea, on_delete=models.SET_NULL, null=True, blank=True)
    table = models.ForeignKey(Table, on_delete=models.SET_NULL, null=True, blank=True )
    special_notes = models.TextField(default="Null")
    created = models.DateTimeField(default=now, blank=True, null=True)
    payment_mode = models.CharField(default="NO PAYMENT", max_length=50, choices=pay_mode)
    transaction_id = models.CharField(blank=True, null=True, max_length=100)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    updated = models.DateField(auto_now=True, blank=True, null=True)

    class Meta:
        ordering = ['-created']

    def __str__(self):
        if self.table and self.dining_area:
            return f"Order {self.random_id} for Table {self.table.table_number} in {self.dining_area.name} - {self.created}"
        elif self.table:
            return f"Order {self.random_id} for Table {self.table.table_number} - {self.created}"
        else:
            return f"Order {self.random_id} - {self.created}"



class OrderItem(models.Model):
    ORDER_TYPE_CHOICES = [
        ('Dine-In', 'Dine-In'),
        ('Take-Away', 'Take-Away'),
    ]
    
    SPECIAL_NOTES_CHOICES = [
        ('strongly spiced', 'strongly spiced'),
        ('midly spiced', 'midly spiced'),
       ( 'chips' , 'chips'),
       ('rice','rice'),
        ('posho', 'posho'),
       ( 'rice_posho','rice_posho' ),
        ('chips_rice', 'chips_rice'),
       ( 'rice_posho', 'rice_posho'),
        ('chips_posho', 'chips_posho')
    ]
    order = models.ForeignKey(OrderTransaction, on_delete=models.CASCADE, related_name='order_items')
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE, null=True, blank=True)
    order_date = models.DateTimeField(default=now)
    customer_name = models.CharField(max_length=255, blank=True, null=True, default="FishPoint Customer")
    dining_area = models.ForeignKey(DiningArea, on_delete=models.SET_NULL, null=True, blank=True)
    table = models.ForeignKey(Table, on_delete=models.SET_NULL, null=True, blank=True)
    total_price =  models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    quantity = models.IntegerField(blank=True, null=True)
    status = models.CharField(
        max_length=50, default='Pending',
        choices=[('Pending', 'Pending'), ('Preparing', 'Preparing'), ('Cooked', 'Completed'), ('Served', 'Served'), ('Cancelled', 'Cancelled')]
    )
    special_notes = models.CharField(
        default="nothing",
        max_length=50, blank=True, null=True,
        choices=SPECIAL_NOTES_CHOICES
        )
    order_type = models.CharField(
        max_length=10,
        choices=ORDER_TYPE_CHOICES,
        default='Dine-In'
    )
    updated = models.DateField(auto_now=True, blank=True, null=True)
    
    def save(self, *args, **kwargs):
        if self.menu_item and self.quantity:
            try:
                price = Decimal(self.menu_item.price or 0)
                # price = self.menu_item.price
                print(f'The price is {price}')
            except (InvalidOperation, TypeError):
                price = Decimal('0.00')

            try:
                quantity = int(self.quantity or 0)
            except (ValueError, TypeError):
                quantity = 0

            self.total_price = price * quantity
        else:
            self.total_price = total_price

        super().save(*args, **kwargs)


    class Meta:
        verbose_name = 'Order Item'
        verbose_name_plural = 'Order Items'
        ordering = ['-order_date']

    def __str__(self):
        return f"OrderItem {self.id} for Order {self.order.id}"



