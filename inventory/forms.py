from django import forms
from .models import  OrderTransaction, OrderItem, Category
from .models import OrderItem, MenuItem, Category, DiningArea, Table





class OrderForm(forms.ModelForm):
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        label="Category",
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'category-select'})
    )
    menu_item = forms.ModelChoiceField(
        queryset=MenuItem.objects.none(),  # Initially empty
        label="Menu Item",
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'menu-item-select'})
    )

    class Meta:
        model = OrderItem
        fields = [
            'order',
            'category',
            'menu_item',
            'customer_name',
            'quantity',
            'status',
            'special_notes',
            'order_type',
        ]
        widgets = {
            'order': forms.Select(attrs={'class': 'form-control'}),
            'customer_name': forms.TextInput(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
             'special_notes': forms.Select(attrs={'class': 'form-control'}),
            'order_type': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter orders to only show those created today
        from django.utils.timezone import localdate  # Import here to avoid circular imports
        today = localdate()

         # Order by latest transaction (highest id)
        self.fields['order'].queryset = OrderTransaction.objects.filter(created=today).order_by('-id')


        # Filter menu items based on the selected category
        if 'category' in self.data:
            try:
                category_id = int(self.data.get('category'))
                self.fields['menu_item'].queryset = MenuItem.objects.filter(category_id=category_id)
            except (ValueError, TypeError):
                self.fields['menu_item'].queryset = MenuItem.objects.none()
        elif self.instance.pk and self.instance.category:
            self.fields['menu_item'].queryset = self.instance.category.menu_items.all()


class OrderTransactionForm(forms.ModelForm):

    class Meta:
        model = OrderTransaction
        fields = ['customer_name', 'table']
        widgets = {

            
            'table': forms.Select(attrs={'class': 'form-control'}),
            'customer_name': forms.TextInput(attrs={'class': 'form-control'}),
        }




class OrderStatusUpdateForm(forms.ModelForm):
    class Meta:
        model = OrderItem
        fields = ['status',]
        widgets = {
            'status': forms.Select(attrs={'class': 'form-control'}),
        }

class OrderStatusUpdateForm(forms.ModelForm):
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        label="Category",
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'category-select'})
    )
    menu_item = forms.ModelChoiceField(
        queryset=MenuItem.objects.none(),  # Initially empty
        label="Menu Item",
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'menu-item-select'})
    )

    class Meta:
        model = OrderItem
        fields = [
            'order',
            'category',
            'menu_item',
            'customer_name',
            'quantity',
            'status',
            'special_notes',
            'order_type',
        ]
        widgets = {
            'order': forms.Select(attrs={'class': 'form-control'}),
            'customer_name': forms.TextInput(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'special_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'order_type': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'category' in self.data:
            try:
                category_id = int(self.data.get('category'))
                self.fields['menu_item'].queryset = MenuItem.objects.filter(category_id=category_id)
            except (ValueError, TypeError):
                self.fields['menu_item'].queryset = MenuItem.objects.none()
        elif self.instance.pk:
            self.fields['menu_item'].queryset = MenuItem.objects.filter(category=self.instance.menu_item.category)


class OrderTransactionPaymentForm(forms.ModelForm):
    class Meta:
        model = OrderTransaction
        fields = ['payment_mode', 'transaction_id']

        widgets = {
            'payment_mode': forms.Select(attrs={'class': 'form-control'}),
            'transaction_id': forms.TextInput(attrs={'class': 'form-control', 'placeholder':'Leave Blank if Cash Payment'}),
        }
        
        
#ADMIN

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields =['name', 'description', 'grouping']
        widgets ={
            'name':forms.TextInput(attrs={'class':'form-control'}),
            'description':forms.Textarea(attrs={'class':'form-control'}),
            'grouping':forms.Select(attrs={'class':'form-control'}),
        }  
                
class MenuForm(forms.ModelForm):
    class Meta:
        model = MenuItem
        fields =['name','category','price', 'description']
        widgets ={
            'name':forms.TextInput(attrs={'class':'form-control'}),
            'category':forms.Select(attrs={'class':'form-control'}),
            'description':forms.Textarea(attrs={'class':'form-control'}),
            'price':forms.NumberInput(attrs={'class': 'form-control'}),
        }                  
                