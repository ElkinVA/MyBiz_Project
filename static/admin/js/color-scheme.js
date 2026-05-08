// static/admin/js/color-scheme.js
// Визуальный выбор цветовых схем для админки Django
// + автоматическое переключение на custom при ручном изменении цвета

// ==============================================================================
// ✅ ГЛОБАЛЬНЫЙ ФЛАГ ДЛЯ ПРЕДОТВРАЩЕНИЯ ПОВТОРНОЙ ИНИЦИАЛИЗАЦИИ
// ==============================================================================
if (window.colorSchemeInitialized === true) {
    console.log('>>> Color scheme уже инициализирован глобально, пропускаем');
} else {
    window.colorSchemeInitialized = true;

    document.addEventListener('DOMContentLoaded', function() {
        console.log('>>> color-scheme.js DOM загружен');

        // Небольшая задержка для полной загрузки Jazzmin
        setTimeout(function() {
            initializeColorScheme();
        }, 300);
    });
}

function initializeColorScheme() {
    // ✅ ПРОВЕРКА: уже инициализировано в этой сессии
    if (window.colorSchemeSessionInitialized === true) {
        console.log('>>> Color scheme уже инициализирован в сессии, пропускаем');
        return;
    }

    // Проверяем, существует ли поле
    const selectField = document.getElementById('id_color_scheme');
    if (!selectField) {
        console.warn('Поле color_scheme не найдено');
        return;
    }

    // ✅ ПРОВЕРКА: поле уже скрыто (значит уже инициализировано)
    if (selectField.style.display === 'none' && selectField.dataset.colorSchemeInitialized === 'true') {
        console.log('>>> Поле уже скрыто и инициализировано');
        window.colorSchemeSessionInitialized = true;
        return;
    }

    // ✅ ПРОВЕРКА: удаляем все существующие превью-контейнеры (защита от дублей)
    const existingPreviews = document.querySelectorAll('.color-scheme-preview-container');
    if (existingPreviews.length > 1) {
        console.log('>>> Найдено дубликатов превью:', existingPreviews.length, 'удаляем лишние');
        existingPreviews.forEach((preview, index) => {
            if (index > 0) {
                preview.remove();
            }
        });
    } else if (existingPreviews.length === 1) {
        console.log('>>> Превью контейнер уже существует, пропускаем инициализацию');
        window.colorSchemeSessionInitialized = true;
        selectField.dataset.colorSchemeInitialized = 'true';
        return;
    }

    // Помечаем как инициализированное
    window.colorSchemeSessionInitialized = true;
    selectField.dataset.colorSchemeInitialized = 'true';

    // ==========================================================================
    // ✅ ОБНОВЛЁННЫЕ ЦВЕТОВЫЕ СХЕМЫ (header_footer_bg_color теперь гармонирует)
    // ==========================================================================
    const colorSchemes = {
        'wood': {
            primary_color: '#2E5C44',
            secondary_color: '#4F3A2B',
            accent_color: '#A04030',   // обновлено
            text_color: '#1E2B26',
            background_color: '#F3F0E9',
            header_footer_bg_color: '#F5F1E7',
            header_footer_text_color: '#1E2B26',
            hero_bg_color: '#DFD9CE',
            border_color: '#D4C5B0'
        },
        'coffee': {
            primary_color: '#87492E',
            secondary_color: '#684E39',
            accent_color: '#B5651D',   // обновлено
            text_color: '#342015',
            background_color: '#FCF5E8',
            header_footer_bg_color: '#F7EFE2',
            header_footer_text_color: '#342015',
            hero_bg_color: '#F0E2D3',
            border_color: '#E6D5C3'
        },
        'flower': {
            primary_color: '#8F2E55',
            secondary_color: '#624766',
            accent_color: '#B8475E',   // обновлено
            text_color: '#2D232E',
            background_color: '#FEF6F9',
            header_footer_bg_color: '#FDF2F5',
            header_footer_text_color: '#2D232E',
            hero_bg_color: '#FCE4E4',
            border_color: '#F5D5E0'
        },
        'vintage': {
            primary_color: '#5F4F3F',
            secondary_color: '#5F4A3A',
            accent_color: '#A04030',   // обновлено
            text_color: '#31261D',
            background_color: '#EEE7DF',
            header_footer_bg_color: '#F0E6D8',
            header_footer_text_color: '#31261D',
            hero_bg_color: '#DBCFC2',
            border_color: '#D5C5B5'
        },
        'pastel': {
            primary_color: '#2E5454',
            secondary_color: '#7A4F4F',
            accent_color: '#5E4563',   // без изменений
            text_color: '#202A33',
            background_color: '#F9F6F0',
            header_footer_bg_color: '#F4F9F5',
            header_footer_text_color: '#202A33',
            hero_bg_color: '#E2F0F0',
            border_color: '#D8E0E0'
        },
        'custom': null
    };

    const schemeNames = {
        'wood': '🌳 Дерево',
        'coffee': '☕ Кофе',
        'flower': '🌺 Цветок',
        'vintage': '📻 Винтаж',
        'pastel': '🎨 Пастель',
        'custom': '✏️ Пользовательская'
    };

    const schemeHints = {
        'wood': 'Скандинавский минимализм',
        'coffee': 'Итальянское кафе',
        'flower': 'Весенний сад',
        'vintage': 'Бруклинский лофт',
        'pastel': 'Мятная свежесть',
        'custom': 'Настройте цвета вручную'
    };

    // Находим поле выбора схемы по id
    if (!selectField) {
        console.warn('Поле color_scheme не найдено');
        return;
    }

    // ✅ ГАРАНТИРОВАННО СКРЫВАЕМ ОРИГИНАЛЬНОЕ ПОЛЕ
    selectField.style.display = 'none';
    selectField.style.visibility = 'hidden';
    selectField.style.height = '0';
    selectField.style.overflow = 'hidden';
    selectField.setAttribute('aria-hidden', 'true');

    // Находим родительский контейнер для вставки карточек
    const schemeField = selectField.closest('.form-group.field-color_scheme') ||
                        selectField.closest('.form-row') ||
                        selectField.parentNode;
    if (!schemeField) {
        console.warn('Родительский контейнер для color_scheme не найден');
        return;
    }

    // ✅ ПРОВЕРКА: не создан ли уже превью-контейнер
    const existingPreview = schemeField.querySelector('.color-scheme-preview-container');
    if (existingPreview) {
        console.log('>>> Превью контейнер уже существует в DOM');
        return;
    }

    // Получаем текущую схему
    const currentScheme = selectField.value || 'wood';

    // Создаём контейнер предпросмотра
    const previewContainer = document.createElement('div');
    previewContainer.className = 'color-scheme-preview-container';
    previewContainer.id = 'color-scheme-preview-container';

    // Генерируем карточки динамически из данных
    let optionsHtml = '';
    for (const [scheme, colors] of Object.entries(colorSchemes)) {
        const isActive = (scheme === currentScheme) ? 'active' : '';
        const name = schemeNames[scheme] || scheme;
        const hint = schemeHints[scheme] || '';

        // Создаём цветовые полосы
        let colorsHtml = '';
        if (scheme === 'custom') {
            colorsHtml = `
                <div class="color-scheme-color" style="background: linear-gradient(135deg, #667eea, #764ba2);" title="Primary"></div>
                <div class="color-scheme-color" style="background: linear-gradient(135deg, #764ba2, #f093fb);" title="Secondary"></div>
                <div class="color-scheme-color" style="background: linear-gradient(135deg, #f093fb, #f5576c);" title="Accent"></div>
                <div class="color-scheme-color" style="background: linear-gradient(135deg, #4facfe, #00f2fe);" title="Header/Footer BG"></div>
                <div class="color-scheme-color" style="background: linear-gradient(135deg, #f5af19, #f12711);" title="Header/Footer Text"></div>
                <div class="color-scheme-color" style="background: linear-gradient(135deg, #a8edea, #fed6e3);" title="Hero BG"></div>
            `;
        } else if (colors) {
            colorsHtml = `
                <div class="color-scheme-color" style="background: ${colors.primary_color};" title="Primary"></div>
                <div class="color-scheme-color" style="background: ${colors.secondary_color};" title="Secondary"></div>
                <div class="color-scheme-color" style="background: ${colors.accent_color};" title="Accent"></div>
                <div class="color-scheme-color" style="background: ${colors.header_footer_bg_color}; border: 1px solid #ddd;" title="Header/Footer BG"></div>
                <div class="color-scheme-color" style="background: ${colors.header_footer_text_color};" title="Header/Footer Text"></div>
                <div class="color-scheme-color" style="background: ${colors.hero_bg_color};" title="Hero BG"></div>
            `;
        }

        optionsHtml += `
            <div class="color-scheme-option ${isActive}" data-scheme="${scheme}">
                <div class="color-scheme-colors">
                    ${colorsHtml}
                </div>
                <div class="color-scheme-name">${name}</div>
                <div class="color-scheme-hint">${hint}</div>
            </div>
        `;
    }

    previewContainer.innerHTML = `
        <div class="color-scheme-description">
            <strong>🎨 Текущая схема: ${schemeNames[currentScheme] || 'Дерево'}</strong>
        </div>
        <div class="color-scheme-options">
            ${optionsHtml}
        </div>
    `;

    // Вставляем после поля выбора (или его родителя)
    schemeField.after(previewContainer);

    // Переменная для таймера уведомления
    let notificationTimeout;

    // Функция для переключения на пользовательскую схему
    function setCustomScheme() {
        console.log('setCustomScheme called, current value:', selectField.value);
        if (selectField.value !== 'custom') {
            selectField.value = 'custom';
            selectField.dispatchEvent(new Event('change', { bubbles: true }));
            console.log('Switched to custom');

            // Обновляем активный класс в карточках
            previewContainer.querySelectorAll('.color-scheme-option').forEach(opt => {
                opt.classList.remove('active');
                if (opt.dataset.scheme === 'custom') {
                    opt.classList.add('active');
                }
            });

            // Обновляем описание
            const descriptionElement = previewContainer.querySelector('.color-scheme-description strong');
            if (descriptionElement) {
                descriptionElement.textContent = `🎨 Текущая схема: ${schemeNames['custom']}`;
            }
        }
    }

    // ---- УЛУЧШЕННЫЙ ПОИСК ПОЛЕЙ ЦВЕТА ----
    // Ищем все поля цветов, включая header_footer
    const brandColorFields = [
        'input[name="primary_color"]',
        'input[name="secondary_color"]',
        'input[name="accent_color"]',
        'input[name="text_color"]',
        'input[name="background_color"]',
        'input[name="border_color"]',
        'input[name="header_footer_bg_color"]',
        'input[name="header_footer_text_color"]'
    ].map(selector => document.querySelector(selector)).filter(el => el);

    const colorPickers = document.querySelectorAll('input[type="color"]');
    const hexFields = document.querySelectorAll('input.color-hex-input');

    // Объединяем только поля палитры бренда
    const allColorFields = [...new Set([...brandColorFields, ...colorPickers, ...hexFields])];
    console.log('Найдено полей цвета палитры бренда:', allColorFields.length);

    // Добавляем обработчики на все найденные поля
    allColorFields.forEach(field => {
        // Удаляем старые обработчики, чтобы не было дублей
        field.removeEventListener('input', setCustomScheme);
        field.removeEventListener('change', setCustomScheme);

        // Добавляем новые
        field.addEventListener('input', setCustomScheme);
        field.addEventListener('change', setCustomScheme);
        console.log('Обработчик добавлен для:', field.name || field.type);
    });

    // Обработчики кликов на карточки схем
    previewContainer.querySelectorAll('.color-scheme-option').forEach(option => {
        option.addEventListener('click', function() {
            const scheme = this.getAttribute('data-scheme');

            // Обновляем select
            selectField.value = scheme;
            selectField.dispatchEvent(new Event('change', { bubbles: true }));

            // Обновляем активный класс
            previewContainer.querySelectorAll('.color-scheme-option').forEach(opt => {
                opt.classList.remove('active');
            });
            this.classList.add('active');

            // Заполняем цвета если не custom
            if (scheme !== 'custom' && colorSchemes[scheme]) {
                const colors = colorSchemes[scheme];
                Object.keys(colors).forEach(fieldName => {
                    const input = document.querySelector(`input[name="${fieldName}"]`);
                    if (input) {
                        input.value = colors[fieldName];
                        input.dispatchEvent(new Event('change', { bubbles: true }));
                        input.dispatchEvent(new Event('input', { bubbles: true }));
                    }
                });
            }

            // Обновляем описание
            const descriptionElement = previewContainer.querySelector('.color-scheme-description strong');
            if (descriptionElement) {
                descriptionElement.textContent = `🎨 Текущая схема: ${schemeNames[scheme] || scheme}`;
            }

            // Показываем уведомление
            showNotification(schemeNames[scheme] || scheme);
        });
    });

    function showNotification(schemeName) {
        // Очищаем предыдущий таймер
        if (notificationTimeout) {
            clearTimeout(notificationTimeout);
        }

        // Удаляем старые уведомления
        const existing = document.querySelector('.scheme-notification');
        if (existing) existing.remove();

        const notification = document.createElement('div');
        notification.className = 'scheme-notification';
        notification.innerHTML = `
            <span>✅ Схема "${schemeName}" применена</span>
            <button class="notification-close">&times;</button>
        `;

        notification.querySelector('.notification-close').onclick = function() {
            notification.style.animation = 'slideOut 0.3s ease-out';
            notificationTimeout = setTimeout(() => notification.remove(), 300);
        };

        document.body.appendChild(notification);

        // Автоудаление через 3 секунды
        notificationTimeout = setTimeout(() => {
            if (notification.parentNode) {
                notification.style.animation = 'slideOut 0.3s ease-out';
                setTimeout(() => notification.remove(), 300);
            }
        }, 3000);
    }

    console.log('>>> Color scheme инициализирован успешно');
}
