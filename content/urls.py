# content/urls.py
from django.urls import path
from . import views

app_name = 'content'

urlpatterns = [
    path('newsletter/subscribe/', views.newsletter_subscribe, name='newsletter_subscribe'),
    path('contact/', views.contact_form, name='contact_form'),
    path('stock-notify/<int:product_id>/', views.stock_notify, name='stock_notify'),
    path('promotions/', views.PromotionListView.as_view(), name='promotions_list'),
]
