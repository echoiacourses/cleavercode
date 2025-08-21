
from django.urls import path
from . import views

from django.conf import settings
from django.contrib.staticfiles.urls import staticfiles_urlpatterns, static

urlpatterns = [
    # path('', views.home, name='index'),
    path('', views.HomeListView.as_view(), name='index'),
    # path('product/<int:pk>/', views.product_details, name='product-details'),
    # path('product/<int:pk>/', views.ProductDetailView.as_view(), name='product-details'),
    path('product/<slug>/', views.ProductDetailView.as_view(), name='product-details'),
    path("category/<int:pk>/", views.CategoryListView.as_view(), name="category-detail"),
]

