from django import forms
from .models import OtherPackage
from django.contrib.admin.widgets import AdminDateWidget

class OtherPackageForm(forms.ModelForm):
    class Meta:
        model = OtherPackage
        fields = '__all__'
        exclude = ['created_by']
        widgets = {
            'start_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'end_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Bootstrap classes
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})
        
        # Special handling for datetime fields
        self.fields['start_time'].widget.attrs['class'] = 'form-control datetimepicker'
        self.fields['end_time'].widget.attrs['class'] = 'form-control datetimepicker'