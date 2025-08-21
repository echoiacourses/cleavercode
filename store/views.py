from django.shortcuts import render

from django.views.generic import ListView, DetailView, TemplateView
from .models import Category, Product, ProductImages, Banner, Offer
# Create your views here.

class HomeListView(TemplateView):
    banners = Banner.objects.filter(is_active=True).order_by('-id')[0:4]
    product_categories = Category.objects.all()[:5]
    offer_products = Offer.objects.filter(is_offer=True).order_by('-created')
    def get(self, request, *args, **kwargs):
        products = Product.objects.all().order_by('-id')
        return render(request, 'index.html',{
            'products':products,
            'banners':self.banners,
            'product_categories':self.product_categories,
            'offer_products':self.offer_products,
        })
    
    def post(self, request, *args, **kwargs):
        if request.method == 'post' or request.method == 'POST':
            search_product = request.POST.get('search_product')
            products = Product.objects.filter(name__icontains=search_product).order_by('-id')

        return render(request, 'index.html',{
            'products':products,
            'banners':self.banners,
            'product_categories':self.product_categories,
            'offer_products':self.offer_products,
        })  



# class HomeListView(ListView):
#     model = Product
#     template_name = 'index.html'
#     context_object_name = 'products'

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['banners'] = Banner.objects.filter(is_active=True).order_by('-id')[0:4]
#         return context
    
class ProductDetailView(DetailView):
    model = Product
    template_name = 'product.html'
    context_object_name = 'item'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['product_images'] = ProductImages.objects.filter(product=self.object.id)
        return context

# def product_details(request, pk):
#     item = Product.objects.get(id=pk)
#     return render(request,'product.html',{
#         'item':item
#     })



# def home(request):
#     return render(request,'index.html',{})


# for the categories

class CategoryListView(ListView):
    model = Product
    template_name = "category_product_list.html"
    context_object_name = "products"
    paginate_by = 6

    def get_queryset(self):
        return (Product.objects
                .filter(category__pk=self.kwargs["pk"])
                .select_related("category"))

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["category"] = Category.objects.get(pk=self.kwargs["pk"])
        ctx["banners"] = Banner.objects.filter(is_active=True).order_by('-id')[0:4]
        ctx["product_categories"] = Category.objects.all()[:5]
        ctx["offer_products"] = Offer.objects.filter(is_offer=True).order_by('-created')

        return ctx