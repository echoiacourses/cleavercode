
from django.urls import path
from . import views

from django.conf import settings
from django.contrib.staticfiles.urls import staticfiles_urlpatterns, static

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.Customerlogin, name='login'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('logout/', views.Customerlogout, name='logout'),
]

