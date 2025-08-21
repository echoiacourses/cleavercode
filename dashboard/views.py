from django.shortcuts import render, redirect, get_object_or_404

from django.views.generic import TemplateView, ListView, DetailView
from django.views.generic.edit import DeleteView

from store.models import Product, Category
from store.forms import ProductForm, CategoryForm
from order.models import Order
from payment.models import BillingAddress

from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
# Create your views here.

# this is for deshboard index
class DashboardIndexView(TemplateView):
    def get(self, request, *args, **kwargs):
        return render(request, 'dashboard_index.html')

    def post(self, request, *args, **kwargs):
        pass

# this is for product view
class ProductListView(TemplateView):
    def get(self, request, *args, **kwargs):
        products = Product.objects.all().order_by('-id')
        return render(request, 'dashboard_product_list.html',{
            'products':products
        })

    def post(self, request, *args, **kwargs):
        pass

class AddNewProduct(TemplateView):
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            if request.user.user_type == 'developer':
                form = ProductForm()
                return render(request, 'add_form.html', {
                    'form':form
                })
            else:
                return redirect('index')
            
        else:
            return redirect('index')
    
    def post(self, request, *args, **kwargs):
        if request.user.user_type == 'developer':
            if request.method == 'post' or request.method == 'POST':
                form = ProductForm(request.POST, request.FILES)
                if form.is_valid():
                    product = form.save(commit=False)
                    slug = product.name.replace(' ','-')
                    product.slug=slug.lower()
                    product.save() 

                    return redirect('product_list')
            else:
                return redirect('index')
        else:
            return redirect('index')

class ProductUpdateView(TemplateView):
    def get(self, request, slug, *args, **kwargs):
        product = Product.objects.get(slug = slug)
        form = ProductForm(instance=product)
        return render(request, 'add_form.html', {
            'form':form
        }) 
    
    def post(self, request, slug, *args, **kwargs):
        if request.user.user_type == 'developer':
            if request.method == 'post' or request.method == 'POST':
                product_ins = Product.objects.get(slug = slug)
                form = ProductForm(request.POST, request.FILES, instance=product_ins)
                if form.is_valid():
                    product = form.save(commit=False)
                    slug = product.name.replace(' ','-')
                    product.slug=slug.lower()
                    product.save() 

                    return redirect('product_list')
            else:
                return redirect('index')
        else:
            return redirect('index')
        
# class ProductDeleteView(DeleteView):
#     model = Product
#     success_url = 'product_list' 

class ProductDeleteView(TemplateView):
    def get(self, request, slug, *args, **kwargs):
        product = Product.objects.get(slug=slug)
        product.delete()
        return redirect('product_list')
    
# category view
class CategoryListView(ListView):
    model = Category
    template_name = 'dashboard_category_list.html'
    context_object_name = 'categories'

class AddNewcategory(TemplateView):
    def get(self, request, *args, **kwargs):
        if request.user.user_type == 'developer':
            form = CategoryForm()
            return render(request, 'add_form.html', {
                'form':form
            })
        else:
            return redirect('index')

    def post(self, request, *args, **kwargs):
        if request.user.user_type == 'developer':
            if request.method == 'post' or request.method == 'POST':
                form = CategoryForm(request.POST, request.FILES)
                if form.is_valid():
                    form.save()
                    return redirect('category_list')
            else:
                return redirect('index')
        else:
            return redirect('index')


class CategoryUpdateView(TemplateView):
    def get(self, request, pk, *args, **kwargs):
        category = Category.objects.get(id = pk)
        form = CategoryForm(instance=category)
        return render(request, 'add_form.html', {
            'form':form
        }) 
    
    def post(self, request, pk, *args, **kwargs):
        if request.user.user_type == 'developer':
            if request.method == 'post' or request.method == 'POST':
                category = Category.objects.get(id=pk)
                form = CategoryForm(request.POST, request.FILES, instance=category)
                if form.is_valid():
                    form.save()
                    return redirect('category_list')
            else:
                return redirect('index')
        else:
            return redirect('index')
        
class CategoryDeleteView(TemplateView):
    def get(self, request, pk, *args, **kwargs):
        category = Category.objects.get(id=pk)
        category.delete()
        return redirect('category_list')
    

class OrderListView(ListView):
    model = Order
    template_name = 'dashboard_order_list.html'
    context_object_name = 'orders'

    def get_queryset(self):
        # only completed orders; pull user + items efficiently
        return (Order.objects
                .filter(ordered=True)
                .select_related('user')
                .prefetch_related('orderitems'))
    

class OrderDetailView(DetailView):
    model = Order
    template_name = 'dashboard_order_detail.html'
    context_object_name = 'order'

    def get_queryset(self):
        # order → user, and prefetch orderitems + the product on each cart row
        return (Order.objects
                .select_related('user')
                .prefetch_related('orderitems__item'))

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        order = self.object
        ctx['billing'] = BillingAddress.objects.filter(user=order.user).first()
        ctx['profile'] = getattr(order.user, 'profile', None)  # safe if missing
        ctx['items'] = order.orderitems.all()
        return ctx
@login_required
def order_ship(request, pk):
    if not (request.user.is_staff or getattr(request.user, 'user_type', '') == 'developer'):
        messages.error(request, "You don't have permission to ship orders.")
        return redirect('order_detail', pk=pk)

    if request.method == 'POST':
        order = get_object_or_404(Order, pk=pk)
        if not order.shipped:
            order.shipped = True
            order.shipped_at = timezone.now()
            order.save(update_fields=['shipped', 'shipped_at'])
            messages.success(request, "Order marked as shipped.")
    return redirect('order_detail', pk=pk)



# @login_required
# def order_ship(request, pk):
#     # allow only admins/developers
#     if not (request.user.is_staff or getattr(request.user, 'user_type', '') == 'developer'):
#         messages.error(request, "You don't have permission to ship orders.")
#         return redirect('order_detail', pk=pk)

#     if request.method == 'POST':
#         order = get_object_or_404(Order, pk=pk)
#         if not order.shipped:
#             order.shipped = True
#             order.shipped_at = timezone.now()
#             order.save(update_fields=['shipped', 'shipped_at'])
#             messages.success(request, "Order marked as shipped.")
#         else:
#             messages.info(request, "Order is already shipped.")
#     return redirect('order_detail', pk=pk)