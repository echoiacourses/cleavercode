from django.shortcuts import render, redirect, get_object_or_404
from store.models import Product
from order.models import Cart, Order
from django.contrib.auth.decorators import login_required

from coupon.models import Coupon
from coupon.forms import CouponCodeForm

from django.utils import timezone

from notification.notific import SendNotification
# Create your views here.



@login_required(login_url='login')
def add_to_cart(request, pk):
    item = get_object_or_404(Product, pk=pk)

    # 1) read form values first
    size = request.POST.get('size') or None
    color = request.POST.get('color') or None
    try:
        quantity = max(1, int(request.POST.get('quantity') or 1))
    except (TypeError, ValueError):
        quantity = 1

    order_qs = Order.objects.filter(user=request.user, ordered=False)

    if order_qs.exists():
        order = order_qs[0]

        # 2) include size/color in get_or_create; set initial qty via defaults
        order_item, created = Cart.objects.get_or_create(
            user=request.user,
            item=item,
            size=size,
            color=color,
            purchased=False,
            defaults={'quantity': quantity},
        )

        if not created:
            order_item.quantity += quantity
            order_item.save()
            message = f"Quantity Updated"
            SendNotification(request.user, message)

        # 3) attach by pk so we tie the exact variant
        if not order.orderitems.filter(pk=order_item.pk).exists():
            order.orderitems.add(order_item)

        return redirect('index')

    else:
        order = Order.objects.create(user=request.user, ordered=False)

        order_item, created = Cart.objects.get_or_create(
            user=request.user,
            item=item,
            size=size,
            color=color,
            purchased=False,
            defaults={'quantity': quantity},
        )
        if not created:
            order_item.quantity += quantity
            order_item.save()

        order.orderitems.add(order_item)
        message = f"Product added to Your cart"
        SendNotification(request.user, message)
        return redirect('index')

# @login_required(login_url='login')
# def add_to_cart(request, pk):
#     item = get_object_or_404(Product, pk=pk)
#     order_item = Cart.objects.get_or_create(item=item, user=request.user, purchased=False)
#     order_qs = Order.objects.filter(user=request.user, ordered=False)
#     if order_qs.exists():
#         order = order_qs[0]
#         if order.orderitems.filter(item=item).exists():
#             size = request.POST.get('size')
#             color = request.POST.get('color')
#             quantity = request.POST.get('quantity')
#             if quantity:
#                 order_item[0].quantity += int(quantity)
#             else:
#                 order_item[0].quantity += 1
#             order_item[0].size = size
#             order_item[0].color = color
#             order_item[0].save()
#             return redirect('index')
#         else:
#             size = request.POST.get('size')
#             color = request.POST.get('color')
#             order_item[0].size = size
#             order_item[0].color = color
#             order_item[0].save()
            
#             order.orderitems.add(order_item[0])
#             return redirect('index')
#     else:
#         size = request.POST.get('size')
#         color = request.POST.get('color')
#         quantity = request.POST.get('quantity')

#         order = Order.objects.create(user=request.user, ordered=False)

#         # order_item = Cart.objects.create(
#         #     user=request.user,
#         #     item=item,                     # <-- REQUIRED (was missing)
#         #     size=size,
#         #     color=color,
#         #     quantity=quantity,
#         #     purchased=False,
#         # )
#         order_item[0].size=size
#         order_item[0].color=color
#         order_item[0].quantity=int(quantity)

#         order.orderitems.add(order_item[0])
#         order.save()
#         order_item[0].save()
#         return redirect('index')    


def cart_view(request):
    if request.user.is_authenticated:
        carts = Cart.objects.filter(user=request.user, purchased= False)
        orders = Order.objects.filter(user=request.user, ordered= False) 
        if carts.exists() and orders.exists():
            order = orders[0]
            coupon_form = CouponCodeForm(request.POST)
            if coupon_form.is_valid():
                current_time = timezone.now()
                code = coupon_form.cleaned_data.get('code')
                coupon_obj = Coupon.objects.get(code=code)
                if coupon_obj.valid_to>=current_time and coupon_obj.active== True:
                    get_discount = (coupon_obj.discount/100)*order.get_totals()
                    total_price_after_discount = order.get_totals() - get_discount
                    request.session['discount_total']=total_price_after_discount
                    request.session['coupon_code']=code
                    return redirect('cart')
            total_price_after_discount=request.session.get('discount_total')
            coupon_code=request.session.get('coupon_code')
            
            if total_price_after_discount and coupon_code:
                return render(request, 'cart.html',{
                    "carts":carts,
                    "order":order,
                    "coupon_form":coupon_form,
                    "total_price_after_discount":total_price_after_discount,
                    "coupon_code":coupon_code,  
                })
            else:
                return render(request, 'cart.html',{
                    "carts":carts,
                    "order":order,
                    "coupon_form":coupon_form     
                })
        else:
            return redirect('index')    
    else:
        return redirect('login')
    
def remove_item_from_cart(request, pk):
    item = get_object_or_404(Product, pk=pk)
    orders = Order.objects.filter(user=request.user, ordered=False)
    if orders.exists():
        order=orders[0]
        if order.orderitems.filter(item=item).exists():
            order_item = Cart.objects.filter(item=item, user=request.user, purchased=False)[0]
            order.orderitems.remove(order_item)
            order_item.delete()
            return redirect('cart')
        else:
            return redirect('cart')
    else:
        return redirect('cart')
    

def increase_cart(request, pk):
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]

        # 🔁 change: pk refers to Cart row, not Product
        order_item = get_object_or_404(Cart, pk=pk, user=request.user, purchased=False)

        # optional safety: ensure this line is in the open order
        if not order.orderitems.filter(pk=order_item.pk).exists():
            return redirect('index')

        if order_item.quantity >= 1:
            order_item.quantity += 1
            order_item.save()
            return redirect('cart')
        else:
            return redirect('index')
    else:
        return redirect('index')


def decrease_cart(request, pk):
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]

        # 🔁 change: pk refers to Cart row, not Product
        order_item = get_object_or_404(Cart, pk=pk, user=request.user, purchased=False)

        # optional safety
        if not order.orderitems.filter(pk=order_item.pk).exists():
            return redirect('index')

        if order_item.quantity > 1:
            order_item.quantity -= 1
            order_item.save()
            return redirect('cart')
        else:
            order.orderitems.remove(order_item)
            order_item.delete()
            return redirect('cart')
    else:
        return redirect('index')

# def increase_cart(request, pk):
#     item = get_object_or_404(Product, pk=pk)
#     order_qs = Order.objects.filter(user=request.user, ordered=False)
#     if order_qs.exists():
#         order = order_qs[0]
#         if order.orderitems.filter(item=item).exists():
#             order_item = Cart.objects.filter(item=item, user=request.user, purchased=False)[0]
#             if order_item.quantity >=1:
#                 order_item.quantity+=1
#                 order_item.save()
#                 return redirect('cart')
#         else:
#             return redirect('index')
#     else:
#         return redirect('index')
            

# def decrease_cart(request, pk):
#     item = get_object_or_404(Product, pk=pk)
#     order_qs = Order.objects.filter(user=request.user, ordered=False)
#     if order_qs.exists():
#         order = order_qs[0]
#         if order.orderitems.filter(item=item).exists():
#             order_item = Cart.objects.filter(item=item, user=request.user, purchased=False)[0]
#             if order_item.quantity >1:
#                 order_item.quantity-=1
#                 order_item.save()
#                 return redirect('cart')
#             else:
#                 order.orderitems.remove(order_item)
#                 order_item.delete()
#                 return redirect('cart')
#         else:
#             return redirect('index')
#     else:
#         return redirect('index')
            


