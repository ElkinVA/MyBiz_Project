from django.urls import path, re_path
from . import views

app_name = 'mybiz_core'

urlpatterns = [
    path('', views.home, name='home'),
    path('products/', views.product_list, name='product_list'),
    path('products/load-more/', views.load_more_products, name='load_more_products'),
    re_path(r'^products/category/(?P<category_slug>[-\w]+)/$', views.product_list, name='product_list_by_category'),
    re_path(r'^products/(?P<product_slug>[-\w]+)/$', views.product_detail, name='product_detail'),
]
