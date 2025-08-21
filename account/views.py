from django.shortcuts import render, HttpResponse, redirect
from account.forms import RegistrationForm

# authentication function
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate, get_user_model


from order.models import Cart, Order
from payment.models import BillingAddress
from payment.forms import BillingAddressForm
from .models import Profile
from .forms import ProfileForm

from django.views.generic import TemplateView
from django.contrib import messages
# Create your views here.

User = get_user_model()

def register(request):
    if request.user.is_authenticated:
        return redirect('profile')

    if request.method == 'POST':
        email = (request.POST.get('email') or '').strip().lower()
        username = (request.POST.get('username') or '').strip()
        pw1 = request.POST.get('password1') or ''
        pw2 = request.POST.get('password2') or ''

        if not email or not username or not pw1 or not pw2:
            messages.error(request, 'Please fill in all fields.')
            return redirect('index')

        if pw1 != pw2:
            messages.error(request, "Passwords don't match.")
            return redirect('index')

        if User.objects.filter(email=email).exists():
            messages.error(request, 'This email is already registered.')
            return redirect('index')

        if User.objects.filter(user_name=username).exists():
            messages.error(request, 'This username is already taken.')
            return redirect('index')

        user = User.objects.create_user(
            email=email, user_name=username, password=pw1, is_active=True
        )
        login(request, user)
        return redirect('profile')

    # GET: just show the page that contains your modal
    return render(request, 'index.html', {})

# def register(request):
#     if request.user.is_authenticated:
#         return HttpResponse('You are authenticated')
#     else:
#         form = RegistrationForm()
#         if request.method == 'post' or request.method == 'POST':
#             form = RegistrationForm(request.POST)
#             if form.is_valid():
#                 form.save()
#                 return HttpResponse('Your account has been created')
    

#     return render(request,'register.html',{'form':form})

def Customerlogin(request):
    if request.user.is_authenticated:
        return HttpResponse('You are Logged in')
    else:
        if request.method == 'post' or request.method == 'POST':
            username = request.POST.get('username')
            password = request.POST.get('password')
            customer = authenticate(request, username=username, password=password)
            if customer is not None:
                login(request, customer)
                return redirect('profile')
            else:
                messages.success(request, 'No such Users')
                return redirect('index')

    return render(request,'index.html',{})

def Customerlogout(request):
    if request.user.is_authenticated:
        logout(request)
        return redirect('index') 

class ProfileView(TemplateView):
    def get(self, request, *args, **kwargs):
        orders = Order.objects.filter(user=request.user, ordered=True)
        billingaddress = BillingAddress.objects.filter(user=request.user).first()
        billingaddress_form = BillingAddressForm(instance=billingaddress)

        profile_obj = Profile.objects.get(user=request.user)
        profileform = ProfileForm(instance=profile_obj)

        return render(request, 'profile.html', {
            'orders':orders,
            'billingaddress':billingaddress,
            'billingaddress_form':billingaddress_form,
            'profileform':profileform
        })

    def post(self, request, *args, **kwargs):
        billingaddress = BillingAddress.objects.filter(user=request.user).first()
        billingaddress_form = BillingAddressForm(request.POST, instance=billingaddress)

        profile_obj = Profile.objects.get(user=request.user)
        profileform = ProfileForm(request.POST ,instance=profile_obj)

        if billingaddress_form.is_valid() and profileform.is_valid():
            addr = billingaddress_form.save(commit=False)
            if addr.user_id is None:          # <- minimal fix
                addr.user = request.user
            addr.save()
            profileform.save()
            return redirect('profile')