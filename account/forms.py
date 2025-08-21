from django.forms import ModelForm
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm 
from .models import Profile
from django import forms

class ProfileForm(ModelForm):
    class Meta:
        model = Profile
        fields = ("__all__")
        exclude = ("user",)  # we set this in the view
        widgets = {
            "full_name": forms.TextInput(attrs={"class": "form-control", "placeholder": "First name"}),
            "address": forms.TextInput(attrs={"class": "form-control", "placeholder": "Last name"}),
            "country": forms.TextInput(attrs={"class": "form-control", "placeholder": "Country"}),
            "city": forms.Textarea(attrs={"class": "form-control", "rows": 2, "placeholder": "Street address"}),
            "zipcode": forms.Textarea(attrs={"class": "form-control", "rows": 2, "placeholder": "Apartment, suite, etc. (optional)"}),
            "phone": forms.TextInput(attrs={"class": "form-control", "placeholder": "City"}),
        }    

class RegistrationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('email','username','password1','password2')
