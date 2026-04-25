"""
REST API views для MyBiz проекта.
"""
from rest_framework import viewsets, filters, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticatedOrReadOnly, AllowAny
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from django.shortcuts import get_object_or_404

from mybiz_core.models import Category, Product
from content.models import Promotion, SiteSettings, NewsletterSubscriber
from .serializers import (
    CategorySerializer, CategoryListSerializer,
    ProductSerializer, ProductListSerializer,
    PromotionSerializer, SiteSettingsSerializer
)


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 12
    page_size_query_param = 'page_size'
    max_page_size = 100


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.filter(is_active=True).prefetch_related('children')
    permission_classes = [AllowAny]
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at', 'products_count']

    def get_serializer_class(self):
        if self.action == 'list':
            return CategoryListSerializer
        return CategorySerializer


class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Product.objects.filter(is_active=True).select_related('category')
    permission_classes = [AllowAny]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = {
        'category': ['exact'],
        'category__slug': ['exact'],
        'price': ['gte', 'lte'],
        'in_stock': ['exact'],
        'is_new': ['exact'],
        'is_featured': ['exact'],
        'brand': ['exact'],
    }
    search_fields = ['name', 'short_description', 'description', 'sku', 'brand']
    ordering_fields = ['price', 'created_at', 'rating', 'name']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'list':
            return ProductListSerializer
        return ProductSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        in_stock = self.request.query_params.get('in_stock_only')
        if in_stock and in_stock.lower() == 'true':
            queryset = queryset.filter(in_stock=True, stock__gt=0)
        has_discount = self.request.query_params.get('has_discount')
        if has_discount and has_discount.lower() == 'true':
            queryset = queryset.filter(discount_price__isnull=False)
        return queryset


class PromotionViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [AllowAny]
    pagination_class = StandardResultsSetPagination
    serializer_class = PromotionSerializer

    def get_queryset(self):
        from django.utils import timezone
        today = timezone.now().date()
        queryset = Promotion.objects.filter(
            is_active=True,
            start_date__lte=today
        ).filter(
            Q(end_date__gte=today) | Q(end_date__isnull=True)
        ).order_by('-created_at')
        return queryset


@api_view(['GET'])
@permission_classes([AllowAny])
def site_settings(request):
    settings = SiteSettings.load()
    serializer = SiteSettingsSerializer(settings)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([AllowAny])
def newsletter_subscribe(request):
    email = request.data.get('email')
    if not email:
        return Response({'error': 'Email обязателен'}, status=status.HTTP_400_BAD_REQUEST)
    try:
        from django.core.validators import validate_email
        validate_email(email)
    except Exception:
        return Response({'error': 'Некорректный email'}, status=status.HTTP_400_BAD_REQUEST)
    subscriber, created = NewsletterSubscriber.objects.get_or_create(
        email=email,
        defaults={'is_active': True}
    )
    if created:
        return Response({'message': 'Вы успешно подписались на рассылку!'}, status=status.HTTP_201_CREATED)
    else:
        if not subscriber.is_active:
            subscriber.is_active = True
            subscriber.save()
            return Response({'message': 'Подписка восстановлена!'}, status=status.HTTP_200_OK)
        return Response({'message': 'Этот email уже подписан на рассылку.'}, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    from django.db import connection
    from django.core.cache import cache
    health_status = {'status': 'healthy', 'database': 'ok', 'cache': 'ok'}
    try:
        connection.ensure_connection()
    except Exception as e:
        health_status['database'] = f'error: {str(e)}'
        health_status['status'] = 'unhealthy'
    try:
        cache.set('health_check', 'ok', 1)
        cache.get('health_check')
    except Exception as e:
        health_status['cache'] = f'error: {str(e)}'
        health_status['status'] = 'unhealthy'
    status_code = status.HTTP_200_OK if health_status['status'] == 'healthy' else status.HTTP_503_SERVICE_UNAVAILABLE
    return Response(health_status, status=status_code)
