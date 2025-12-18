# mybiz_core/tests_validation.py
from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from .models import Product, Category
from .validators import validate_image_extension, validate_image_size

class ImageValidationTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(
            name="Test Category",
            slug="test-category"
        )

    def test_valid_image_extension(self):
        """Тест валидного расширения изображения"""
        valid_image = SimpleUploadedFile(
            "test.jpg",
            b"file_content",
            content_type="image/jpeg"
        )
        # Не должно вызывать исключение
        validate_image_extension(valid_image)

    def test_invalid_image_extension(self):
        """Тест невалидного расширения изображения"""
        invalid_image = SimpleUploadedFile(
            "test.txt",
            b"file_content",
            content_type="text/plain"
        )
        with self.assertRaises(Exception):
            validate_image_extension(invalid_image)

    def test_image_size_too_large(self):
        """Тест слишком большого изображения"""
        # Создаем файл больше 5MB
        large_content = b"x" * (6 * 1024 * 1024)  # 6MB
        large_image = SimpleUploadedFile(
            "large.jpg",
            large_content,
            content_type="image/jpeg"
        )
        with self.assertRaises(Exception):
            validate_image_size(large_image)

    def test_product_image_validation(self):
        """Тест загрузки изображения для товара"""
        # Валидное изображение
        valid_image = SimpleUploadedFile(
            "product.jpg",
            b"valid_image_content",
            content_type="image/jpeg"
        )

        product = Product(
            name="Test Product",
            slug="test-product",
            description="Test description",
            price=1000,
            category=self.category,
            image=valid_image
        )

        # Не должно вызывать исключение при валидации
        product.full_clean()
