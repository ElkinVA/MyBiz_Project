# mybiz_core/urls.py
from django.urls import path
from . import views

app_name = 'mybiz_core'

urlpatterns = [
    path('', views.home, name='home'),
    path('products/', views.product_list, name='product_list'),
    # Используем <str:...> вместо <slug:...> для поддержки кириллицы в URL
    path('products/category/<str:category_slug>/', views.product_list, name='product_list_by_category'),
    path('products/<int:pk>/<str:slug>/', views.product_detail, name='product_detail'),
]
