from django import forms
from .models import Address

class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ['email', 'username', 'mobile', 'address', 'city', 'state', 'zip_code']
        widgets = {
            'mobile': forms.TextInput(attrs={'placeholder': 'Enter mobile number'})
        }

