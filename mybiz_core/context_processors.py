from .models import Category


def categories(request):
    """Добавляет список активных категорий в контекст всех шаблонов."""
    return {
        'categories': Category.objects.filter(is_active=True).order_by('name')
    }
