"""
Тесты для моделей content (SiteSettings, Promotion и др.)
"""
import pytest
from decimal import Decimal
from content.models import SiteSettings, Promotion


@pytest.mark.django_db
class TestSiteSettingsModel:
    """Тесты модели SiteSettings"""

    def test_sitesettings_creation(self):
        """Проверка создания настроек сайта"""
        settings = SiteSettings.objects.create(
            site_name='Test Site',
            site_tagline='Test Tagline',
            color_scheme='wood'
        )
        assert settings.site_name == 'Test Site'
        assert settings.color_scheme == 'wood'
        assert str(settings) == 'Test Site'

    def test_sitesettings_singleton(self):
        """Проверка что создается только один экземпляр настроек"""
        settings1 = SiteSettings.load()
        settings2 = SiteSettings.load()
        assert settings1.pk == settings2.pk

    def test_sitesettings_color_scheme_wood_applies_colors(self):
        """Проверка что схема 'wood' применяет цвета"""
        settings = SiteSettings.objects.create(
            site_name='Test',
            color_scheme='wood'
        )
        # Проверяем что цвета установлены согласно схеме wood
        assert settings.primary_color == '#2E5C44'
        assert settings.secondary_color == '#4F3A2B'
        assert settings.accent_color == '#D9734C'

    def test_sitesettings_color_scheme_coffee_applies_colors(self):
        """Проверка что схема 'coffee' применяет цвета"""
        settings = SiteSettings.objects.create(
            site_name='Test',
            color_scheme='coffee'
        )
        assert settings.primary_color == '#87492E'
        assert settings.secondary_color == '#684E39'
        assert settings.accent_color == '#E6B17E'

    def test_sitesettings_color_scheme_custom_preserves_colors(self):
        """Проверка что схема 'custom' сохраняет пользовательские цвета"""
        # Создаем настройки с пользовательской схемой и своими цветами
        settings = SiteSettings.objects.create(
            site_name='Test Custom',
            color_scheme='custom',
            primary_color='#FF0000',
            secondary_color='#00FF00',
            accent_color='#0000FF',
            text_color='#111111',
            background_color='#FFFFFF',
            header_bg_color='#EEEEEE',
            header_text_color='#333333',
            footer_bg_color='#222222',
            hero_bg_color='#DDDDDD',
            border_color='#CCCCCC'
        )
        
        # Проверяем что цвета сохранились как задано
        assert settings.primary_color == '#FF0000'
        assert settings.secondary_color == '#00FF00'
        assert settings.accent_color == '#0000FF'
        assert settings.text_color == '#111111'
        assert settings.background_color == '#FFFFFF'

    def test_sitesettings_change_to_custom_preserves_current_colors(self):
        """Проверка что при переключении на 'custom' цвета не меняются"""
        # Сначала создаем с готовой схемой
        settings = SiteSettings.objects.create(
            site_name='Test',
            color_scheme='wood'
        )
        original_primary = settings.primary_color
        assert original_primary == '#2E5C44'
        
        # Меняем цвет вручную на валидный HEX
        settings.primary_color = '#CC0000'
        settings.color_scheme = 'custom'
        settings.save()
        
        # Перезагружаем из БД
        settings.refresh_from_db()
        
        # Проверяем что цвет остался пользовательским
        assert settings.primary_color == '#CC0000'
        assert settings.color_scheme == 'custom'

    def test_sitesettings_change_from_custom_to_scheme_applies_colors(self):
        """Проверка что при переключении с 'custom' на схему применяются цвета схемы"""
        settings = SiteSettings.objects.create(
            site_name='Test',
            color_scheme='custom',
            primary_color='#FF0000'
        )
        
        # Переключаемся на схему wood
        settings.color_scheme = 'wood'
        settings.save()
        
        # Перезагружаем из БД
        settings.refresh_from_db()
        
        # Проверяем что цвета применились от схемы wood
        assert settings.primary_color == '#2E5C44'
        assert settings.color_scheme == 'wood'

    def test_sitesettings_get_scheme_colors_by_name(self):
        """Проверка метода get_scheme_colors_by_name"""
        wood_colors = SiteSettings.get_scheme_colors_by_name('wood')
        assert wood_colors['primary_color'] == '#2E5C44'
        
        coffee_colors = SiteSettings.get_scheme_colors_by_name('coffee')
        assert coffee_colors['primary_color'] == '#87492E'
        
        custom_colors = SiteSettings.get_scheme_colors_by_name('custom')
        assert custom_colors == {}
        
        # Несуществующая схема возвращает wood
        unknown_colors = SiteSettings.get_scheme_colors_by_name('unknown')
        assert unknown_colors['primary_color'] == '#2E5C44'

    def test_sitesettings_hex_color_validation(self):
        """Проверка валидации HEX цветов"""
        from django.core.exceptions import ValidationError
        
        # Создаем объект с невалидным цветом и схемой custom (чтобы не перезаписался)
        settings = SiteSettings(
            site_name='Test',
            color_scheme='custom',
            primary_color='invalid_color'
        )
        with pytest.raises(ValidationError):
            settings.save()

    def test_sitesettings_short_hex_color_expands(self):
        """Проверка что короткие HEX цвета расширяются до полных"""
        settings = SiteSettings.objects.create(
            site_name='Test',
            color_scheme='custom',
            primary_color='#F00',  # Короткий формат
        )
        # После сохранения короткий формат должен расшириться
        settings.refresh_from_db()
        assert settings.primary_color == '#FF0000'


@pytest.mark.django_db
class TestPromotionModel:
    """Тесты модели Promotion"""

    def test_promotion_creation(self):
        """Проверка создания промо-акции"""
        from django.core.files.uploadedfile import SimpleUploadedFile
        
        image = SimpleUploadedFile("test.jpg", b"file_content", content_type="image/jpeg")
        promotion = Promotion.objects.create(
            title='Test Promotion',
            description='Test Description',
            image=image
        )
        assert promotion.title == 'Test Promotion'
        assert promotion.is_active is True
        assert promotion.discount_type == 'percent'
        assert promotion.discount_value == Decimal('0')

    def test_promotion_apply_discount_percent(self):
        """Проверка применения процентной скидки"""
        from django.core.files.uploadedfile import SimpleUploadedFile
        
        image = SimpleUploadedFile("test.jpg", b"file_content", content_type="image/jpeg")
        promotion = Promotion.objects.create(
            title='Test',
            description='Test',
            image=image,
            discount_type='percent',
            discount_value=Decimal('20.00')
        )
        
        price = Decimal('1000')
        discounted_price = promotion.apply_discount(price)
        assert discounted_price == Decimal('800')

    def test_promotion_apply_discount_fixed(self):
        """Проверка применения фиксированной скидки"""
        from django.core.files.uploadedfile import SimpleUploadedFile
        
        image = SimpleUploadedFile("test.jpg", b"file_content", content_type="image/jpeg")
        promotion = Promotion.objects.create(
            title='Test',
            description='Test',
            image=image,
            discount_type='fixed',
            discount_value=Decimal('200.00')
        )
        
        price = Decimal('1000')
        discounted_price = promotion.apply_discount(price)
        assert discounted_price == Decimal('800')

    def test_promotion_slug_auto_generation(self):
        """Проверка автогенерации slug"""
        from django.core.files.uploadedfile import SimpleUploadedFile
        
        image = SimpleUploadedFile("test.jpg", b"file_content", content_type="image/jpeg")
        promotion = Promotion.objects.create(
            title='Тестовая акция',
            description='Test',
            image=image
        )
        # Slug генерируется с использованием кириллицы (allow_unicode=True)
        assert promotion.slug == 'тестовая-акция'
