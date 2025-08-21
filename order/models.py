from django.db import models
# from django.contrib.auth.models import User
from django.contrib.auth import get_user_model

from store.models import Product, VariationValue

# Create your models here.

User = get_user_model()

class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cart')
    item = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    size = models.CharField(max_length=100, blank=True, null=True)
    color = models.CharField(max_length=100, blank=True, null=True)
    purchased = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.quantity} X {self.item}"
    
    def get_total(self):
        total = self.item.price * self.quantity
        float_total = format(total, '0.2f')
        return float_total
    
    def variation_single_price(self):
        sizes = VariationValue.objects.filter(variation='size', product=self.item)
        colors = VariationValue.objects.filter(variation='color', product=self.item)

        size_price = 0
        color_price = 0

        # If a size is selected and exists in DB
        if sizes.exists():
            for size in sizes:
                if size.name == self.size:
                    size_price = size.price
                    break

        # If a color is selected and exists in DB
        if colors.exists():
            for color in colors:
                if color.name == self.color:
                    color_price = color.price
                    break

        total = size_price + color_price

        # Fallback: if both are 0, use product's base price
        if total == 0:
            total = self.item.price

        return format(total, '0.2f')
        
    def variation_total(self):
        sizes = VariationValue.objects.filter(variation='size', product=self.item)
        colors = VariationValue.objects.filter(variation='color', product=self.item)

        size_price = 0
        color_price = 0

        total_size_price = 0
        total_color_price = 0

        # If a size is selected and exists in DB
        if sizes.exists():
            for size in sizes:
                if size.name == self.size:
                    size_price = size.price
                    total_size_price = size_price * self.quantity
                    break

        # If a color is selected and exists in DB
        if colors.exists():
            for color in colors:
                if color.name == self.color:
                    color_price = color.price
                    total_color_price = color_price * self.quantity
                    break

        total = total_size_price + total_color_price

        # Fallback: if both are 0, use product's base price
        if total == 0:
            total = self.item.price * self.quantity

        return format(total, '0.2f')    


class Order(models.Model):
    PAYMENT_METHOD = (
        ('Cash on Delivery','Cash on Delivery',),
        ('Paypal','Paypal'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    orderitems = models.ManyToManyField(Cart)
    ordered = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    payment_id = models.CharField(max_length=255, blank=True, null=True)
    order_id = models.CharField(max_length=255, blank=True, null=True)
    payment_method = models.CharField(max_length=30, choices=PAYMENT_METHOD, default='Cash on Delivery')

    shipped = models.BooleanField(default=False)
    shipped_at = models.DateTimeField(blank=True, null=True)
    def get_totals(self):
        total = 0
        for order_item in self.orderitems.all():
            total+= float(order_item.variation_total())
        return total
    


    def __str__(self):
        return super().__str__()

