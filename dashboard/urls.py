from django.urls import path
from . import views


urlpatterns = [
    path('index/', views.DashboardIndexView.as_view(), name='dashboard_index'),
    path('products/', views.ProductListView.as_view(), name='product_list'),
    path('product/add-new/', views.AddNewProduct.as_view(), name='add_new_product'),
    path('product/update/<slug:slug>', views.ProductUpdateView.as_view(), name='product_update'),
    path('product/delete/<slug:slug>', views.ProductDeleteView.as_view(), name='product_delete'),
    path('categories/', views.CategoryListView.as_view(), name='category_list'),
    path('category/add-new/', views.AddNewcategory.as_view(), name='add_new_category'),
    path('category/update/<int:pk>', views.CategoryUpdateView.as_view(), name='category_update'),
    path('category/delete/<int:pk>', views.CategoryDeleteView.as_view(), name='category_delete'),
    path('orderlist/', views.OrderListView.as_view(), name='order_list'),
    path('orders/<int:pk>/', views.OrderDetailView.as_view(), name='order_detail'),  # ← new
    path('orders/<int:pk>/ship/', views.order_ship, name='order_ship'),  
]

