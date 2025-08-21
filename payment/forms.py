from django import forms
from .models import BillingAddress
from order.models import Order


class BillingAddressForm(forms.ModelForm):

    class Meta:
        model = BillingAddress
        fields = ["user", "first_name", "last_name", "country", "address1", "address2", "city", "zipcode", "phone_number"]
        exclude = ("user",)  # we set this in the view
        widgets = {
            "first_name": forms.TextInput(attrs={"class": "form-control", "placeholder": "First name"}),
            "last_name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Last name"}),
            "country": forms.TextInput(attrs={"class": "form-control", "placeholder": "Country"}),
            "address1": forms.Textarea(attrs={"class": "form-control", "rows": 2, "placeholder": "Street address"}),
            "address2": forms.Textarea(attrs={"class": "form-control", "rows": 2, "placeholder": "Apartment, suite, etc. (optional)"}),
            "city": forms.TextInput(attrs={"class": "form-control", "placeholder": "City"}),
            "zipcode": forms.TextInput(attrs={"class": "form-control", "placeholder": "ZIP / Postal code"}),
            "phone_number": forms.TextInput(attrs={"class": "form-control", "placeholder": "Phone number"}),
        }

class PaymentMethodForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['payment_method']
        widgets = {
            "payment_method": forms.Select(attrs={"class": "form-select", "placeholder": "Payment Method"}),
        }