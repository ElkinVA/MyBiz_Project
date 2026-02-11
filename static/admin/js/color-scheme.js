// static/admin/js/color-scheme.js - исправленный
document.addEventListener('DOMContentLoaded', function() {
    // Определяем новые цветовые схемы с правильными именами полей
    const colorSchemes = {
        'wood': {
            primary_color: '#2e8b57',
            secondary_color: '#8b7355',
            accent_color: '#d2691e',
            text_color: '#2f4f4f',
            background_color: '#f5f5f5',
            header_bg_color: '#ffffff',
            footer_bg_color: '#556b2f',
            hero_bg_color: '#8fbc8f'
        },
        'coffee': {
            primary_color: '#6f4e37',
            secondary_color: '#8b7355',
            accent_color: '#d2691e',
            text_color: '#3e2723',
            background_color: '#fff8e1',
            header_bg_color: '#5d4037',
            footer_bg_color: '#3e2723',
            hero_bg_color: '#a1887f'
        },
        'flower': {
            primary_color: '#e91e63',
            secondary_color: '#9c27b0',
            accent_color: '#ff9800',
            text_color: '#5d4037',
            background_color: '#fff3e0',
            header_bg_color: '#fce4ec',
            footer_bg_color: '#9c27b0',
            hero_bg_color: '#f8bbd0'
        },
        'vintage': {
            primary_color: '#8d6e63',
            secondary_color: '#a1887f',
            accent_color: '#5d4037',
            text_color: '#4e342e',
            background_color: '#efebe9',
            header_bg_color: '#d7ccc8',
            footer_bg_color: '#5d4037',
            hero_bg_color: '#bcaaa4'
        },
        'pastel': {
            primary_color: '#f8bbd0',
            secondary_color: '#c5cae9',
            accent_color: '#80deea',
            text_color: '#546e7a',
            background_color: '#fce4ec',
            header_bg_color: '#f3e5f5',
            footer_bg_color: '#b39ddb',
            hero_bg_color: '#e1bee7'
        },
        'custom': {
            primary_color: '',
            secondary_color: '',
            accent_color: '',
            text_color: '',
            background_color: '',
            header_bg_color: '',
            footer_bg_color: '',
            hero_bg_color: ''
        }
    };

    // Функция для добавления кнопок быстрого предпросмотра
    function addQuickPreviewButtons() {
        const schemeField = document.querySelector('.form-row.field-color_scheme');
        if (!schemeField) return;

        const previewContainer = document.createElement('div');
        previewContainer.className = 'color-scheme-options';
        previewContainer.innerHTML = `
            <div class="color-scheme-option" data-scheme="wood">
                <div class="color-scheme-colors">
                    <div class="color-scheme-color" style="background: #2e8b57;" title="Primary"></div>
                    <div class="color-scheme-color" style="background: #8b7355;" title="Secondary"></div>
                    <div class="color-scheme-color" style="background: #d2691e;" title="Accent"></div>
                    <div class="color-scheme-color" style="background: #2f4f4f;" title="Text"></div>
                    <div class="color-scheme-color" style="background: #f5f5f5;" title="Background"></div>
                </div>
                <div class="color-scheme-name">Дерево</div>
                <div class="color-scheme-hint">Натуральные тона</div>
            </div>
            <div class="color-scheme-option" data-scheme="coffee">
                <div class="color-scheme-colors">
                    <div class="color-scheme-color" style="background: #6f4e37;" title="Primary"></div>
                    <div class="color-scheme-color" style="background: #8b7355;" title="Secondary"></div>
                    <div class="color-scheme-color" style="background: #d2691e;" title="Accent"></div>
                    <div class="color-scheme-color" style="background: #3e2723;" title="Text"></div>
                    <div class="color-scheme-color" style="background: #fff8e1;" title="Background"></div>
                </div>
                <div class="color-scheme-name">Кофе</div>
                <div class="color-scheme-hint">Теплые оттенки</div>
            </div>
            <div class="color-scheme-option" data-scheme="flower">
                <div class="color-scheme-colors">
                    <div class="color-scheme-color" style="background: #e91e63;" title="Primary"></div>
                    <div class="color-scheme-color" style="background: #9c27b0;" title="Secondary"></div>
                    <div class="color-scheme-color" style="background: #ff9800;" title="Accent"></div>
                    <div class="color-scheme-color" style="background: #5d4037;" title="Text"></div>
                    <div class="color-scheme-color" style="background: #fff3e0;" title="Background"></div>
                </div>
                <div class="color-scheme-name">Цветок</div>
                <div class="color-scheme-hint">Яркие цвета</div>
            </div>
            <div class="color-scheme-option" data-scheme="vintage">
                <div class="color-scheme-colors">
                    <div class="color-scheme-color" style="background: #8d6e63;" title="Primary"></div>
                    <div class="color-scheme-color" style="background: #a1887f;" title="Secondary"></div>
                    <div class="color-scheme-color" style="background: #5d4037;" title="Accent"></div>
                    <div class="color-scheme-color" style="background: #4e342e;" title="Text"></div>
                    <div class="color-scheme-color" style="background: #efebe9;" title="Background"></div>
                </div>
                <div class="color-scheme-name">Винтаж</div>
                <div class="color-scheme-hint">Классические тона</div>
            </div>
            <div class="color-scheme-option" data-scheme="pastel">
                <div class="color-scheme-colors">
                    <div class="color-scheme-color" style="background: #f8bbd0;" title="Primary"></div>
                    <div class="color-scheme-color" style="background: #c5cae9;" title="Secondary"></div>
                    <div class="color-scheme-color" style="background: #80deea;" title="Accent"></div>
                    <div class="color-scheme-color" style="background: #546e7a;" title="Text"></div>
                    <div class="color-scheme-color" style="background: #fce4ec;" title="Background"></div>
                </div>
                <div class="color-scheme-name">Пастель</div>
                <div class="color-scheme-hint">Мягкие тона</div>
            </div>
        `;

        // Вставляем контейнер после поля выбора схемы
        const selectField = schemeField.querySelector('select');
        if (selectField && selectField.parentNode) {
            selectField.parentNode.after(previewContainer);
        }

        // Добавляем обработчики кликов
        previewContainer.querySelectorAll('.color-scheme-option').forEach(option => {
            option.addEventListener('click', function() {
                const scheme = this.getAttribute('data-scheme');
                selectField.value = scheme;

                // Обновляем предварительный просмотр
                previewContainer.querySelectorAll('.color-scheme-option').forEach(opt => {
                    opt.classList.remove('active');
                });
                this.classList.add('active');

                // Если не custom, заполняем цвета
                if (scheme !== 'custom' && colorSchemes[scheme]) {
                    const colors = colorSchemes[scheme];
                    Object.keys(colors).forEach(fieldName => {
                        const input = document.querySelector(`input[name="${fieldName}"]`);
                        if (input && colors[fieldName]) {
                            input.value = colors[fieldName];

                            // Обновляем цветовой пикер если он есть
                            const colorPicker = input.closest('.color-picker-container');
                            if (colorPicker) {
                                const hexInput = colorPicker.querySelector('.color-hex-input');
                                if (hexInput) {
                                    hexInput.value = colors[fieldName];
                                }
                                const colorInput = colorPicker.querySelector('input[type="color"]');
                                if (colorInput) {
                                    colorInput.value = colors[fieldName];
                                }
                            }
                        }
                    });

                    // Показываем уведомление об успешном применении
                    showSchemeAppliedNotification(scheme);
                }

                // Триггерим событие change для select
                const event = new Event('change', { bubbles: true });
                selectField.dispatchEvent(event);
            });
        });

        // Помечаем активную схему
        const currentScheme = selectField.value;
        const activeOption = previewContainer.querySelector(`[data-scheme="${currentScheme}"]`);
        if (activeOption) {
            activeOption.classList.add('active');
        }
    }

    // Функция для показа уведомления
    function showSchemeAppliedNotification(schemeName) {
        const schemeNames = {
            'wood': '🌳 Дерево',
            'coffee': '☕ Кофе',
            'flower': '🌺 Цветок',
            'vintage': '📻 Винтаж',
            'pastel': '🎨 Пастель',
            'custom': '✏️ Пользовательская тема'
        };

        // Создаем уведомление
        const notification = document.createElement('div');
        notification.className = 'scheme-notification';
        notification.innerHTML = `
            <div class="notification-content">
                <span>Цветовая схема "${schemeNames[schemeName]}" применена</span>
                <button class="notification-close">&times;</button>
            </div>
        `;

        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: #4CAF50;
            color: white;
            padding: 15px 20px;
            border-radius: 5px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            z-index: 10000;
            animation: slideIn 0.3s ease-out;
        `;

        notification.querySelector('.notification-close').onclick = function() {
            notification.style.animation = 'slideOut 0.3s ease-in';
            setTimeout(() => notification.remove(), 300);
        };

        document.body.appendChild(notification);

        // Автоматически скрываем через 3 секунды
        setTimeout(() => {
            if (notification.parentNode) {
                notification.style.animation = 'slideOut 0.3s ease-in';
                setTimeout(() => notification.remove(), 300);
            }
        }, 3000);
    }

    // Добавляем CSS анимации для уведомлений
    const style = document.createElement('style');
    style.textContent = `
        @keyframes slideIn {
            from { transform: translateX(100%); opacity: 0; }
            to { transform: translateX(0); opacity: 1; }
        }
        @keyframes slideOut {
            from { transform: translateX(0); opacity: 1; }
            to { transform: translateX(100%); opacity: 0; }
        }

        .notification-content {
            display: flex;
            align-items: center;
            justify-content: space-between;
        }

        .notification-close {
            background: none;
            border: none;
            color: white;
            font-size: 20px;
            cursor: pointer;
            margin-left: 10px;
            padding: 0;
            line-height: 1;
        }

        .notification-close:hover {
            opacity: 0.8;
        }
    `;
    document.head.appendChild(style);

    // Инициализация при загрузке страницы
    addQuickPreviewButtons();

    // Слушаем изменения в select для обновления активной опции
    const schemeSelect = document.querySelector('select[name="color_scheme"]');
    if (schemeSelect) {
        schemeSelect.addEventListener('change', function() {
            const scheme = this.value;
            const previewContainer = document.querySelector('.color-scheme-options');
            if (previewContainer) {
                previewContainer.querySelectorAll('.color-scheme-option').forEach(opt => {
                    opt.classList.remove('active');
                });
                const activeOption = previewContainer.querySelector(`[data-scheme="${scheme}"]`);
                if (activeOption) {
                    activeOption.classList.add('active');
                }
            }
        });
    }
});
