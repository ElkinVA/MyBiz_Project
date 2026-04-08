"""
URL маршруты для REST API.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    CategoryViewSet,
    ProductViewSet,
    PromotionViewSet,
    site_settings,
    newsletter_subscribe,
    health_check
)

router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'products', ProductViewSet, basename='product')
router.register(r'promotions', PromotionViewSet, basename='promotion')

urlpatterns = [
    path('', include(router.urls)),
    path('site-settings/', site_settings, name='api-site-settings'),
    path('newsletter/subscribe/', newsletter_subscribe, name='api-newsletter-subscribe'),
    path('health/', health_check, name='api-health-check'),
]
