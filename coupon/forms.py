from django import forms


class CouponCodeForm(forms.Form):
    code = forms.CharField(
        label='',
        max_length=32,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Coupon code',
        })
    )