from django.urls import re_path
from . import views

app_name = 'pages'

urlpatterns = [
    re_path(r'^pages/(?P<page_slug>[-\w]+)/$', views.page_detail, name='page_detail'),
]
