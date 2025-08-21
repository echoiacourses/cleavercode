from django.db import models
from django.urls import reverse

from django.template.defaultfilters import slugify
from django.contrib.auth import get_user_model

from django.db import models, transaction
# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=50, blank=False, null=False)
    image = models.ImageField(upload_to='category', blank=True, null=True)
    parent = models.ForeignKey('self', related_name='children', on_delete=models.CASCADE, blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['-created',]
        verbose_name_plural = 'Categories'


class Offer(models.Model):
    product   = models.ForeignKey("Product", on_delete=models.CASCADE, related_name="offers")
    is_offer  = models.BooleanField(default=False)          # toggle to apply
    new_price = models.FloatField(blank=True, null=True)    # the price to set on the product
    applied   = models.BooleanField(default=False, editable=False)  # internal guard
    created   = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Offer for {self.product.name}"

    def save(self, *args, **kwargs):
        # save the offer first so it has an ID
        super().save(*args, **kwargs)

        # apply exactly once when toggled on and a new_price is given
        if self.is_offer and not self.applied and self.new_price is not None:
            with transaction.atomic():
                p = self.product
                # move current price to old_price and set the new price
                p.old_price = p.price
                p.price = float(self.new_price)
                p.save(update_fields=["old_price", "price"])

                # mark this offer as applied so it doesn't run again
                self.applied = True
                super().save(update_fields=["applied"])

class Product(models.Model):
    name = models.CharField(max_length=250, blank=False, null=False)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='category')
    preview_desc = models.CharField(max_length=255, verbose_name='Short Descriptions')
    description = models.TextField(max_length=1000, verbose_name='Descriptions')
    image = models.ImageField(upload_to='products', blank=False, null=False)
    price = models.FloatField()
    old_price = models.FloatField(default=0.00, blank=True, null=True)
    is_stock = models.BooleanField(default=True)
    slug = models.SlugField(unique=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['-created',]

    def get_product_url(self):
        return reverse('product-details', kwargs={'slug':self.slug})

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        return super().save(*args, **kwargs)
    
class ProductImages(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    image = models.FileField(upload_to='product_gallery')
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.product.name)

class VariationManager(models.Manager):
    def sizes(self):
        return super(VariationManager, self).filter(variation='size')
    def colors(self):
        return super(VariationManager, self).filter(variation='color')

VARIATIONS_TYPE = (
    ('size','size'),
    ('color','color'),
)

class VariationValue(models.Model):
    variation = models.CharField(max_length=100, choices=VARIATIONS_TYPE)
    name = models.CharField(max_length=50)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    price = models.IntegerField()
    created = models.DateTimeField(auto_now_add=True)

    objects = VariationManager()

    def __str__(self):
        return self.name
    
class Banner(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='banner')
    image = models.ImageField(upload_to='banner')
    is_active = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.product.name
    
User = get_user_model()
class MyLogo(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)    
    image = models.ImageField(upload_to='logo')
    is_active = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.image)

class MyFavicon(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)    
    image = models.ImageField(upload_to='logo')
    is_active = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.image)