from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.conf import settings

from .models import BillingAddress
from .forms import BillingAddressForm, PaymentMethodForm
from order.models import Cart, Order

from django.views.generic import TemplateView


# import some paypal stuff
from django.conf import settings
import json

class CheckoutTemplateView(TemplateView):

    def get(self, request, *args, **kwargs):
        saved_address = BillingAddress.objects.get_or_create(user=request.user or None)
        saved_address = saved_address[0]
        form = BillingAddressForm(instance=saved_address)

        payment_method = PaymentMethodForm()

        order_qs = Order.objects.filter(user=request.user, ordered=False)
        order_item = order_qs[0].orderitems.all()
        order_total = order_qs[0].get_totals()

        pay_meth = request.GET.get('pay_meth')


        return render(request, 'checkout.html', {
            'form':form,
            'order_item':order_item,
            'order_total':order_total,
            'payment_method':payment_method,
            'PAYPAL_CLIENT_ID': settings.PAYPAL_CLIENT_ID,
            'pay_meth':pay_meth
        })

    def post(self, request, *args, **kwargs):
        
        saved_address = BillingAddress.objects.get_or_create(user=request.user)
        saved_address = saved_address[0]
        form = BillingAddressForm(request.POST, instance=saved_address)
        payment_obj = Order.objects.filter(user=request.user, ordered=False)[0]
        payment_form = PaymentMethodForm(request.POST, instance=payment_obj)

        

        if form.is_valid() and payment_form.is_valid():
            form.save()
            pay_menthod = payment_form.save()

            if not saved_address.is_fully_filled():
                return redirect('checkout')
            
            if pay_menthod.payment_method == 'Cash on Delivery':
                order_qs = Order.objects.filter(user=request.user, ordered=False)
                order = order_qs[0]
                order.order_id=order.id
                order.payment_id=pay_menthod.payment_method
                order.ordered = True
                order.save()

                cart_items = Cart.objects.filter(user=request.user, purchased=False)
                for cart_item in cart_items:
                    cart_item.purchased = True
                    cart_item.save()
                print('Order submitted Successfully')
                return redirect('index')
            
            if pay_menthod.payment_method == 'Paypal':
                return redirect(reverse('checkout')+"?pay_meth="+str(pay_menthod.payment_method))

def paypalPaymentMethod(request):
    data = json.loads(request.body)
    order_id = data['order_id']
    payment_id = data['payment_id']
    status = data['status']

    if status == 'COMPLETED':
        if request.user.is_authenticated:
            order_qs = Order.objects.filter(user=request.user, ordered=False)
            order = order_qs[0]
            order.order_id=order_id
            order.payment_id=payment_id
            order.ordered = True
            order.save()

            cart_items = Cart.objects.filter(user=request.user, purchased=False)
            for cart_item in cart_items:
                cart_item.purchased = True
                cart_item.save()
            print('Order submitted Successfully')
        return redirect('index')










# def payment_success(request):
#     return render(request,'payment_success.html',{})

# def payment_failed(request):
#     return render(request,'payment_failed.html',{})

