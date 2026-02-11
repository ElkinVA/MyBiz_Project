# pages/urls.py
from django.urls import path
from . import views

app_name = 'pages'

urlpatterns = [
    path('pages/<slug:page_slug>/', views.page_detail, name='page_detail'),
]
