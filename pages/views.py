from django.shortcuts import render, get_object_or_404
from .models import Page

def page_detail(request, page_slug):
    """Детальная страница SEO-текстового блока"""
    page = get_object_or_404(Page, slug=page_slug, is_active=True)

    context = {
        'page': page,
        'title': page.title,
    }
    return render(request, 'pages/page_detail.html', context)
