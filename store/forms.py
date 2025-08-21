from django.forms.models import ModelForm
from .models import Category, Product, VariationValue, Banner, MyLogo, MyFavicon, Offer
from django import forms

class ProductForm(ModelForm):
    class Meta:
        model = Product
        fields = ('__all__')
        exclude = ('slug',)
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Product name"}),
            "category": forms.Select(attrs={"class": "form-select"}),
            "preview_desc": forms.TextInput(attrs={"class": "form-control", "placeholder": "Short description", "maxlength": "255"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 4, "placeholder": "Full description (max 1000 characters)", "maxlength": "1000"}),
            "image": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "price": forms.NumberInput(attrs={"class": "form-control", "placeholder": "Price", "step": "0.01", "min": "0"}),
            "old_price": forms.NumberInput(attrs={"class": "form-control", "placeholder": "Old price (optional)", "step": "0.01", "min": "0"}),
            "is_stock": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

class CategoryForm(ModelForm):
    class Meta:
        model = Category
        fields = ('__all__')
        exclude = ('created',)
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Category name", "maxlength": "50"}),
            "image": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "parent": forms.Select(attrs={"class": "form-select"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["parent"].empty_label = "— No parent —"        


class OfferForm(ModelForm):
    class Meta:
        model = Offer
        fields = ['product', 'is_offer', 'new_price']   # only show useful fields
        widgets = {
            'product': forms.Select(attrs={'class': 'form-select'}),
            'is_offer': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'new_price': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter discounted price',
                'step': '0.01',  # allow decimals
                'min': '0'
            }),
        }