# mybiz_core/validators.py - исправленный файл
import os
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from PIL import Image
import io
import re
import logging

logger = logging.getLogger(__name__)

def validate_image_extension(value):
    """Проверяет расширение изображения"""
    ext = os.path.splitext(value.name)[1].lower()
    valid_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.svg']
    if ext not in valid_extensions:
        raise ValidationError(
            f'Неподдерживаемый формат файла. Разрешены: {", ".join(valid_extensions)}'
        )

def validate_image_size(value):
    """Проверяет размер изображения (макс 5MB)"""
    max_size = 5 * 1024 * 1024 # 5MB
    if value.size > max_size:
        raise ValidationError(f'Размер файла не должен превышать 5MB. Текущий размер: {value.size / 1024 / 1024:.2f}MB')

def validate_image_dimensions(value, min_width=100, min_height=100):
    """Проверяет минимальные размеры изображения"""
    try:
        # Для файлов SVG PIL не работает напрямую, нужно обработать отдельно
        if hasattr(value, 'name') and value.name.lower().endswith('.svg'):
            # Простая проверка SVG - если файл слишком мал, он вряд ли валиден
            if value.size < 100: # Пример минимального размера для SVG
                raise ValidationError('SVG файл слишком мал, чтобы быть действительным.')
            return # Для SVG пропускаем проверку размеров через PIL

        with Image.open(value) as img:
            width, height = img.size
            if width < min_width or height < min_height:
                raise ValidationError(
                    f'Минимальные размеры изображения: {min_width}x{min_height}px. '
                    f'Текущие размеры: {width}x{height}px.'
                )
    except Exception as e:
        logger.error(f"Ошибка при проверке размеров изображения {value.name}: {e}")
        raise ValidationError('Не удалось прочитать изображение. Убедитесь, что файл не поврежден.')

def validate_slug_format(value):
    """Проверяет формат slug (только латиница, цифры и дефисы)"""
    if not re.match(r'^[a-z0-9]+(?:-[a-z0-9]+)*$', value):
        raise ValidationError(_('Slug может содержать только латинские буквы в нижнем регистре, цифры и дефисы.'))

def validate_price(value):
    """Проверяет цену"""
    if value is None or value < 0:
        raise ValidationError(_('Цена не может быть отрицательной.'))

def validate_stock(value):
    """Проверяет количество на складе"""
    if value is None or value < 0:
        raise ValidationError(_('Количество на складе не может быть отрицательным.'))
