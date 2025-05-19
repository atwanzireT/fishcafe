from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Revenue
from django.utils import timezone
from decimal import Decimal
from inventory.models import OrderTransaction

from otherPackages.models import OtherPackage

@receiver(post_save, sender=OrderTransaction)
def create_revenue_from_order(sender, instance, created, **kwargs):
    if instance.payment_mode != "NO PAYMENT":
        # Prevent duplicates: only create if no existing revenue for this order
        if not Revenue.objects.filter(description__icontains=f"Order {instance.random_id}").exists():
            total_amount = sum(item.total_price for item in instance.order_items.all())

            Revenue.objects.create(
                category='fnb',
                description=f"F&B Payment for Order {instance.random_id}",
                amount=Decimal(total_amount),
                received_from=instance.customer_name or "walk-in",
                date=timezone.now().date(),
                created_by=instance.created_by,
            )



        
@receiver(post_save, sender=OtherPackage)
def add_revenue_on_service_completion(sender, instance, created, **kwargs):
    if instance:
        # Avoid duplicate revenue entries
        description = f"{instance.get_service_type_display()} - {instance.client_name} - {instance.id}"
        if not Revenue.objects.filter(description=description).exists():
            Revenue.objects.create(
                category='other',
                description=description,
                amount=instance.total_amount,
                received_from=instance.client_name,
                date=timezone.now().date(),
                created_by=instance.created_by,
            )