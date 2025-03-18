from django import forms
from .models import Category, Supplier, Product, IssuedProduct, Batch

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Category Name'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Description', 'rows': 3}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = [
            'name', 'category', 'contact_info', 'email', 'phone_number', 
            'address', 'city', 'country', 'is_verified', 'is_active'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Supplier Name'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'contact_info': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Contact Information', 'rows': 3}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number'}),
            'address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Address'}),
            'city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'City'}),
            'country': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Country'}),
            'is_verified': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'category', 'stock_status']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Product Name'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'stock_status': forms.Select(attrs={'class': 'form-control'}),
        }

class BatchForm(forms.ModelForm):
    class Meta:
        model = Batch
        fields = ['product', 'supplier', 'quantity', 'units', 'cost_per_item', 'expiry_date']
        widgets = {
            'product': forms.Select(attrs={'class': 'form-control'}),
            'supplier': forms.Select(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Quantity'}),
            'units': forms.Select(attrs={'class': 'form-control'}),
            'cost_per_item': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Cost per Item'}),
            'expiry_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

    def save(self, commit=True):
        instance = super().save(commit=False)
        # Calculate total cost
        instance.total_cost = instance.quantity * instance.cost_per_item
        if commit:
            instance.save()
        return instance



class IssuedProductForm(forms.ModelForm):
    class Meta:
        model = IssuedProduct
        fields = ['product', 'quantity_taken', 'units', 'person_receiving', 'reason_for_issue']
        widgets = {
            'product': forms.Select(attrs={'class': 'form-control', 'data-live-search': 'true'}),
            'quantity_taken': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Quantity Taken'}),
            'units': forms.Select(attrs={'class': 'form-control'}),
            'person_receiving': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Person Receiving'}),
            'reason_for_issue': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Reason for Issue', 'rows': 3}),
        }
