from django.core.management.base import BaseCommand
from django.core.cache import cache
from content.models import SiteSettings

class Command(BaseCommand):
    help = 'Принудительно обновляет кэш сайта после изменения настроек'

    def handle(self, *args, **options):
        cache.clear()
        settings = SiteSettings.load()
        settings.clear_cache()
        self.stdout.write(self.style.SUCCESS('Кэш успешно очищен'))
