# mybiz_core/validators.py
import os
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from PIL import Image
import io
import re
import logging

logger = logging.getLogger(__name__)

try:
    import defusedxml.ElementTree as ET
    HAS_DEFUSEDXML = True
except ImportError:
    HAS_DEFUSEDXML = False


def validate_image_extension(value):
    """Проверяет расширение изображения"""
    ext = os.path.splitext(value.name)[1].lower()
    valid_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.svg']
    if ext not in valid_extensions:
        raise ValidationError(
            f'Неподдерживаемый формат файла. Разрешены: {", ".join(valid_extensions)}'
        )

    # Дополнительная проверка для SVG
    if ext == '.svg':
        if HAS_DEFUSEDXML:
            try:
                value.seek(0)
                ET.parse(value)
                value.seek(0)
            except Exception:
                raise ValidationError('Некорректный или потенциально опасный SVG файл.')
        else:
            if value.size < 100:
                raise ValidationError('SVG файл слишком мал, чтобы быть действительным.')


def validate_image_size(value):
    """Проверяет размер изображения (макс 5MB)"""
    max_size = 5 * 1024 * 1024  # 5MB
    if value.size > max_size:
        raise ValidationError(
            f'Размер файла не должен превышать 5MB. '
            f'Текущий размер: {value.size / 1024 / 1024:.2f}MB'
        )


def validate_image_dimensions(value, min_width=100, min_height=100):
    """
    Проверяет минимальные размеры изображения.
    ✅ ИСПРАВЛЕНО: Безопасная работа с указателем файла
    """
    try:
        # Для файлов SVG PIL не работает напрямую
        if hasattr(value, 'name') and value.name.lower().endswith('.svg'):
            if value.size < 100:
                raise ValidationError('SVG файл слишком мал, чтобы быть действительным.')
            return

        # Сохраняем позицию до открытия
        original_position = value.tell() if hasattr(value, 'tell') else 0

        with Image.open(value) as img:
            width, height = img.size
            if width < min_width or height < min_height:
                raise ValidationError(
                    f'Минимальные размеры изображения: {min_width}x{min_height}px. '
                    f'Текущие размеры: {width}x{height}px.'
                )

        # Восстанавливаем позицию
        try:
            value.seek(original_position)
        except (AttributeError, IOError):
            pass  # Некоторые storage backend не поддерживают seek

    except Exception as e:
        logger.error(f"Ошибка при проверке размеров изображения {value.name}: {e}")
        raise ValidationError('Не удалось прочитать изображение. Убедитесь, что файл не поврежден.')
