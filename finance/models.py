from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from datetime import date

class Revenue(models.Model):
    REVENUE_CHOICES = [
        ('rooms', 'Rooms'),
        ('fnb', 'Food & Beverage'),
        ('party', 'Party'),
        ('other', 'Other')
    ]
    description = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    date = models.DateField()
    category = models.CharField(max_length=100, blank=True, null=True, choices=REVENUE_CHOICES) 
    attachment = models.FileField(upload_to='attachments/%Y/%m/%d/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    received_from = models.CharField(max_length=30, default="staff")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                                   null=True, blank=True, related_name='+')
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                                   null=True, blank=True, related_name='+')
    def __str__(self):
        return f"Revenue: {self.description} - {self.amount}"


class Expenses(models.Model):
    EXPENSE_CHOICES = [
        ('allowances', 'Allowances'),
        ('purchases', 'Purchases'),
        ('other', 'Other'),
    ]
    name = models.CharField(blank=True, null=True, max_length=200)
    category = models.CharField(
        max_length=100, blank=True, null=True, choices=EXPENSE_CHOICES)
    name_of_supplier = models.CharField(max_length=255)
    
    quantity = models.DecimalField(max_digits=12, decimal_places=2)
    unit_cost = models.DecimalField(max_digits=12, decimal_places=2)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    amount_paid = models.DecimalField(max_digits=12, decimal_places=2)
    balance = models.DecimalField(max_digits=12, decimal_places=2, blank=True)
    is_active = models.BooleanField(default=True)
    created_date = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True)

    def save(self, *args, **kwargs):
        # Automatically calculate balance before saving
        self.total_amount = self.quantity * self.unit_cost
        self.balance = self.total_amount - self.amount_paid
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Expenses: {self.category} - {self.amount_paid}"

class Asset(models.Model):
    name = models.CharField(max_length=255)
    value = models.DecimalField(max_digits=12, decimal_places=2)
    purchase_date = models.DateField(null=True, blank=True)
    life_years = models.PositiveIntegerField(null=True, blank=True)  # expected lifespan for depreciation
    category = models.CharField(max_length=100, blank=True, null=True)
    attachment = models.FileField(upload_to='attachments/%Y/%m/%d/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                                   null=True, blank=True, related_name='+')
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                                   null=True, blank=True, related_name='+')

    @property
    def depreciation_amount(self):
        """Compute depreciation based on value, life_years, and purchase_date."""
        if self.value and self.life_years and self.purchase_date:
            years_passed = (date.today() - self.purchase_date).days / 365.0
            per_year = self.value / self.life_years  # straight-line depreciation per year
            depreciated = per_year * years_passed
            # Cap depreciation between 0 and the asset's value
            depreciated = max(0, min(depreciated, self.value))
            return round(depreciated, 2)
        return 0.0

    def __str__(self):
        return f"Asset: {self.name} - {self.value}"



class Liability(models.Model):
    class LiabilityCategory(models.TextChoices):
        LOAN = 'LOAN', "Loan / Debt"
        PAYABLE = 'PAYABLE', "Accounts Payable"
        OTHER = 'OTHER', "Other"
    description = models.CharField(max_length=255, verbose_name="Liability Description")
    category = models.CharField(max_length=50, choices=LiabilityCategory.choices,
                                default=LiabilityCategory.OTHER, verbose_name="Liability Category")
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    due_date = models.DateField(blank=True, null=True)
    attachment = models.FileField(upload_to="attachments/liability/", blank=True, null=True,
                                  help_text="Supporting document (optional).")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True,
                                   on_delete=models.SET_NULL, related_name="liabilities_created", editable=False)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True,
                                   on_delete=models.SET_NULL, related_name="liabilities_updated", editable=False)
    is_active = models.BooleanField(default=True, verbose_name="Active")

    @property
    def days_overdue(self):
        """Calculate days overdue if not paid by due_date."""
        from datetime import date
        if self.is_active and self.due_date:
            today = date.today()
            if today > self.due_date:
                return (today - self.due_date).days
        return 0

    def __str__(self):
        return f"{self.description} - {self.amount}"

    class Meta:
        verbose_name = "Liability"
        verbose_name_plural = "Liabilities"
        ordering = ["-due_date", "-id"]
