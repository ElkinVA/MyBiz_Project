# 📘 Правила разработки MyBiz (AI-Assistant Guidelines)

Этот документ определяет стандарты кода, архитектуру и рабочие процессы для проекта **MyBiz**.
**Статус:** ✅ Активен. Все новые изменения должны соответствовать этим правилам.

---

## 1. Технологический стек

| Компонент | Требование | Примечание |
| :--- | :--- | :--- |
| **Backend** | Django 5.2+ | Строго. Никаких Flask/FastAPI. |
| **Frontend** | Django Templates + Alpine.js 3.x | ❌ Запрещены: React, Vue, jQuery, SPA. |
| **Стилизация** | Tailwind CSS v3 (mobile-first) | Кастомный CSS только в `static/css/*.css`. |
| **База данных** | Dev: SQLite / Prod: PostgreSQL | В prod: `CONN_MAX_AGE=600`, `sslmode=require`. |
| **Кэширование** | Redis | Для фрагментов, видов и данных сервисов. |
| **Тестирование** | pytest + pytest-django | Структура: `/tests/`. Фикстуры через `factory_boy`. |
| **Браузеры** | Chrome, Firefox, Safari, Edge (latest) | Autoprefixer настроен в сборке. |

---

## 2. Архитектура и именование

### 2.1. Структура приложений
*   `mybiz_core`: Товары (`Product`), Категории (`Category`).
*   `content`: Настройки сайта (`SiteSettings`), Промо (`Promotion`), Подписки, Обратная связь.
*   `pages`: Статические страницы (`Page`).
*   `api`: REST API endpoints (DRF).
*   `services`: Бизнес-логика (сервисный слой), изолированная от View.

### 2.2. URL и View
*   **Маршрутизация:** Строго через `path()` с именованными группами.
*   **Имена путей:** `snake_case` (например, `category_slug`, `product_id`).
*   **Reverse Lookup:** ❌ Запрещён хардкод ссылок. Только `{% url 'namespace:name' arg %}`.
*   **View функции:** `snake_case`, отражают действие (`product_list`, `cart_add`).
*   **Class-based Views:** Стандартные суффиксы (`ListView`, `DetailView`).

```python
# ❌ Плохо
<a href='/products/{{ product.id }}/'>

# ✅ Хорошо
<a href="{% url 'mybiz_core:product_detail' product.slug %}">
```

### 2.3. Модели данных
*   **Наследование:** Все модели наследуют `models.Model`.
*   **Синглтон настроек:** `content.SiteSettings` загружается через `.load()` (кастомный менеджер) или `pk=1`.
*   **Slug:** Обязателен для всех публичных сущностей. Уникальность + метод `_generate_unique_slug()`.
*   **Индексы:** `db_index=True` для полей фильтрации (`is_active`, `slug`, `email`, `created_at`).
*   **Verbose names:** На русском языке для всех полей (`verbose_name="Название товара"`).

```python
# ✅ Пример правильной модели
slug = models.SlugField(unique=True, verbose_name="URL", db_index=True)

def save(self, *args, **kwargs):
    if not self.slug:
        self.slug = self._generate_unique_slug(self.title)
    super().save(*args, **kwargs)
```

---

## 3. Шаблоны и Фронтенд

### 3.1. Базовые принципы
*   Наследование от `base.html`.
*   Использование блоков: `{% block content %}`, `{% block extra_css %}`, `{% block extra_js %}`.
*   **Alpine.js:** Только для интерактивности (модалки, дропдауны, переключатели тем). Не использовать в админке Django.

### 3.2. Тёмная тема
*   Управление классом `dark` на теге `<html>` (Alpine.js + localStorage).
*   Стилизация через префикс `dark:` в Tailwind и CSS-переменные.

### 3.3. Иконки и Изображения
*   **Иконки:** Только через тег `{% social_icon 'name' %}` (загрузка из `social_tags`). ❌ Ручной SVG запрещён.
*   **Изображения:**
    *   Обязательные атрибуты: `width`, `height`, `alt` (осмысленный текст), `loading="lazy"`.
    *   Пользовательский контент: `{% thumbnail image "400x300" crop="center" %}` (sorl-thumbnail).
    *   Формат: Предпочтение WebP с fallback.

### 3.4. Доступность (A11y)
*   Семантический HTML (`<header>`, `<nav>`, `<main>`, `<article>`).
*   Контраст текста ≥ 4.5:1.
*   Интерактивные элементы доступны с клавиатуры (фокус, aria-атрибуты).

---

## 4. Безопасность (🔒 CRITICAL)

### 4.1. Формы и Валидация
*   Все данные пользователя — через `django.forms` (ModelForm).
*   Явное указание полей: `fields = ['title', 'body']` (❌ избегать `__all__` без нужды).
*   Валидация: методы `clean_<field>()` и `clean()`.

### 4.2. Файлы и Изображения
*   Использовать валидаторы из `mybiz_core.validators`:
    *   `validate_image_extension` (.jpg, .png, .webp, .svg).
    *   `validate_image_size` (макс. 5MB).
    *   `validate_image_dimensions` (мин. 100×100).
*   **SVG:** Проверка через `defusedxml`. Запрет скриптов и внешних ссылок.

### 4.3. Защита от атак
*   **CSRF:** `{% csrf_token %}` во всех POST-формах.
*   **XSS:** Фильтр `|safe` ТОЛЬКО для полей после CKEditor. Остальное экранируется автоматически.
*   **Open Redirect:** Использовать утилиту `get_safe_redirect_url()` из `content/views.py`.
    ```python
    # ✅ Хорошо
    return redirect(get_safe_redirect_url(request, next_url))
    ```

### 4.4. Production Headers
В настройках продакшена обязательны:
*   `SECURE_HSTS_SECONDS`
*   `SECURE_SSL_REDIRECT = True`
*   `X_FRAME_OPTIONS = 'DENY'`
*   `SECURE_CONTENT_TYPE_NOSNIFF = True`

---

## 5. Производительность (⚡ CRITICAL)

### 5.1. Работа с БД
*   **N+1 Query:** Строго запрещено. Использовать `select_related` (FK) и `prefetch_related` (M2M/Reverse FK).
*   **Индексы:** Проверять наличие индексов на полях фильтрации и сортировки.

### 5.2. Кэширование
*   **Уровни:**
    1.  Низкоуровневое кэширование (`cache.get/set`) в сервисах и view для тяжелых выборок.
    2.  Кэширование фрагментов шаблонов `{% cache 300 key %} ... {% endcache %}`.
*   **Инвалидация:** Обязательная очистка кэша через сигналы (`post_save`, `post_delete`) при изменении данных.
*   **Ключи:** Должны быть предсказуемыми и включать версию объекта (например, `updated_at`).

### 5.3. Логирование
*   ❌ Запрещён `print()` в коде.
*   ✅ Использовать `logging.getLogger(__name__)`.
*   Уровни: `debug` (отладка), `info` (важные события), `warning` (потенциальные проблемы), `error` (исключения).

---

## 6. Рабочий процесс (Workflow для AI)

1.  **Полнота кода:** При изменении файла предоставлять **полную** версию файла, а не фрагменты с `...`.
2.  **Итеративность:** Сложные задачи разбивать на этапы (MVP -> Рефакторинг -> Оптимизация).
3.  **Миграции:** После изменений моделей явно указывать команды:
    ```bash
    python manage.py makemigrations
    python manage.py migrate
    ```
4.  **Тестирование:**
    *   Новые фичи покрываются тестами в `/tests/`.
    *   Использовать `pytest`, фикстуры и `factory_boy`.
    *   Перед сдачей задачи убедиться, что `pytest` проходит успешно.
5.  **Язык:** Комментарии, докстринги, тексты интерфейса и админки — **на русском языке**.
6.  **Температура генерации:** `temperature=0.0` для детерминированного кода.
7. Ты работаешь в веб версии qwen coder у тебя есть память в /workspace. наша схема работы такая: я из веб версии qwen отправляю изменения, которые ты делаешь, на гитхаб (нажимаю "опубликовать на github"), потом на своем компьютере делаю [
git fetch origin
git checkout main
git merge origin/    + имя ветки
git push origin main]
а ты потом это подгружаешь в /workspace и весь процесс идет заново в цикле [работа в /workspace - github - мой PC - github] 
---

## 7. Обработка исключений

*   **View:** `try-except` только для предсказуемых сценариев (например, `IntegrityError` при уникальности).
*   **Ошибки доступа:** Использовать `get_object_or_404` вместо ручного `try/except DoesNotExist`.
*   **User Feedback:** Для сообщений пользователю использовать `django.contrib.messages`.
*   **Логирование ошибок:** Все необработанные исключения логировать с `exc_info=True`.

```python
# ✅ Хорошо
from django.shortcuts import get_object_or_404
product = get_object_or_404(Product, slug=slug)

# ❌ Плохо
try:
    product = Product.objects.get(slug=slug)
except:
    pass
```

---

## 8. Чек-лист перед коммитом

- [ ] Код соответствует стилю (PEP8, snake_case).
- [ ] Нет хардкода URL (используется `{% url %}`).
- [ ] Добавлены миграции (если менялись модели).
- [ ] Тесты проходят (`pytest`).
- [ ] Нет `print()`, используется логгер.
- [ ] Проверена безопасность (CSRF, валидация файлов, редиректы).
- [ ] Добавлены индексы на поля фильтрации.
- [ ] Реализована инвалидация кэша (если затронуты публичные данные).
