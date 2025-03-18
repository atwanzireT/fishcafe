from django import forms
from .models import Reservation

class ReservationForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = ['event_type', 'name', 'email', 'phone', 'event_date', 'number_of_guests', 'special_requests']
        widgets = {
                'event_type': forms.Select(attrs={'class': 'form-control'}),
                'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Full Name'}),
                'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'you@example.com'}),
                'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number'}),
                'event_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),  # Date picker
                'number_of_guests': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
                'special_requests': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Any special requests'}),
            }