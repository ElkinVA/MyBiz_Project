# mybiz_core/validators.py
import os
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from PIL import Image
import io

def validate_image_extension(value):
    """Проверяет расширение изображения"""
    ext = os.path.splitext(value.name)[1].lower()
    valid_extensions = ['.jpg', '.jpeg', '.png', '.webp', '.gif']

    if ext not in valid_extensions:
        raise ValidationError(
            _('Неподдерживаемый формат изображения. Используйте JPG, PNG, WebP или GIF.')
        )

def validate_image_size(value):
    """Проверяет размер изображения (макс 5MB)"""
    max_size = 5 * 1024 * 1024  # 5MB

    if value.size > max_size:
        raise ValidationError(
            _('Размер изображения не должен превышать 5MB.')
        )

def validate_image_dimensions(value):
    """Проверяет минимальные и максимальные размеры изображения"""
    try:
        # Открываем изображение для проверки размеров
        if hasattr(value, 'temporary_file_path'):
            # Файл сохранен на диске
            img = Image.open(value.temporary_file_path())
        else:
            # Файл в памяти
            if hasattr(value, 'read'):
                img = Image.open(io.BytesIO(value.read()))
                value.seek(0)  # Возвращаем указатель в начало
            else:
                return  # Пропускаем проверку, если не можем прочитать

        min_width, min_height = 300, 300
        max_width, max_height = 5000, 5000

        if img.width < min_width or img.height < min_height:
            raise ValidationError(
                _(f'Минимальный размер изображения: {min_width}x{min_height} пикселей')
            )

        if img.width > max_width or img.height > max_height:
            raise ValidationError(
                _(f'Максимальный размер изображения: {max_width}x{max_height} пикселей')
            )

    except Exception as e:
        # Если не удалось открыть изображение, пропускаем проверку размеров
        # но все равно проверяем расширение и размер файла
        pass

def validate_web_safe_image(value):
    """Проверяет, что изображение безопасно для web"""
    try:
        if hasattr(value, 'temporary_file_path'):
            img = Image.open(value.temporary_file_path())
        else:
            if hasattr(value, 'read'):
                img = Image.open(io.BytesIO(value.read()))
                value.seek(0)
            else:
                return

        # Проверяем режим изображения (RGB, RGBA безопасны)
        if img.mode not in ['RGB', 'RGBA', 'L', 'P']:
            raise ValidationError(
                _('Изображение должно быть в режиме RGB, RGBA или Grayscale.')
            )

        # Проверяем, что это не анимация для статических форматов
        if hasattr(img, 'is_animated') and img.is_animated:
            ext = os.path.splitext(value.name)[1].lower()
            if ext in ['.jpg', '.jpeg', '.png']:
                raise ValidationError(
                    _('Анимированные изображения поддерживаются только в формате GIF.')
                )

    except Exception as e:
        pass
