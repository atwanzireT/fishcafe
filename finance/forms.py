from django import forms
from .models import Revenue, Expenses, Asset, Liability

class RevenueForm(forms.ModelForm):
    class Meta:
        model = Revenue
        fields = ['category', 'description', 'amount', 'received_from', 'date', 'attachment']
        widgets = {
            'category': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'received_from': forms.TextInput(attrs={'class': 'form-control'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'attachment': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }


class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expenses
        fields = ['category', 'name_of_supplier', 'quantity',
                  'unit_cost', 'total_amount', 'amount_paid']
        widgets = {
            'category': forms.Select(attrs={'class': 'form-select'}),
            'name_of_supplier': forms.TextInput(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'unit_cost': forms.NumberInput(attrs={'class': 'form-control'}),
            'total_amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'amount_paid': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class AssetForm(forms.ModelForm):
    class Meta:
        model = Asset
        fields = ['name', 'value', 'purchase_date', 'attachment'] 
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'value': forms.NumberInput(attrs={'class': 'form-control'}),
            'purchase_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}), 
            'attachment': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

class LiabilityForm(forms.ModelForm):
    class Meta:
        model = Liability
        fields = ['description', 'amount', 'due_date', 'attachment']
        widgets = {
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'due_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'attachment': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }