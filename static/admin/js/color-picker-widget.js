// static/admin/js/color-picker-widget.js

document.addEventListener('DOMContentLoaded', function() {
    // Инициализация всех цветовых пикеров на странице
    function initializeColorPickers() {
        const colorPickers = document.querySelectorAll('input[type="color"]');

        colorPickers.forEach(function(picker) {
            // Проверяем, инициализирован ли уже этот пикер
            if (picker.dataset.initialized === 'true') {
                return;
            }

            // Помечаем как инициализированный
            picker.dataset.initialized = 'true';

            // Находим контейнер поля
            const fieldContainer = picker.closest('.fieldBox') || picker.closest('.form-row') || picker.parentNode;

            // Создаем основной контейнер для цветового пикера
            const pickerContainer = document.createElement('div');
            pickerContainer.className = 'color-picker-widget-container';
            pickerContainer.style.cssText = `
                display: flex;
                align-items: center;
                gap: 15px;
                margin: 10px 0;
                padding: 15px;
                background: #f9f9f9;
                border-radius: 8px;
                border: 1px solid #e0e0e0;
            `;

            // Создаем визуальную кнопку для выбора цвета
            const colorButton = document.createElement('div');
            colorButton.className = 'color-picker-visual-button';
            colorButton.style.cssText = `
                width: 60px;
                height: 60px;
                border-radius: 8px;
                background-color: ${picker.value || '#ffffff'};
                border: 3px solid ${picker.value ? darkenColor(picker.value, 0.2) : '#cccccc'};
                cursor: pointer;
                position: relative;
                overflow: hidden;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                transition: all 0.3s ease;
            `;

            // Добавляем эффект при наведении
            colorButton.addEventListener('mouseenter', function() {
                this.style.transform = 'scale(1.05)';
                this.style.boxShadow = '0 4px 10px rgba(0,0,0,0.15)';
            });

            colorButton.addEventListener('mouseleave', function() {
                this.style.transform = 'scale(1)';
                this.style.boxShadow = '0 2px 5px rgba(0,0,0,0.1)';
            });

            // При клике на кнопку открываем нативный пикер
            colorButton.addEventListener('click', function() {
                picker.click();
            });

            // Создаем иконку карандаша для настройки
            const editIcon = document.createElement('div');
            editIcon.innerHTML = `
                <svg style="position: absolute; bottom: 5px; right: 5px; width: 16px; height: 16px;"
                     fill="white" viewBox="0 0 24 24">
                    <path d="M3 17.25V21h3.75L17.81 9.94l-3.75-3.75L3 17.25zM20.71 7.04c.39-.39.39-1.02 0-1.41l-2.34-2.34c-.39-.39-1.02-.39-1.41 0l-1.83 1.83 3.75 3.75 1.83-1.83z"/>
                </svg>
            `;
            colorButton.appendChild(editIcon);

            // Создаем контейнер для информации о цвете
            const infoContainer = document.createElement('div');
            infoContainer.style.cssText = `
                flex-grow: 1;
            `;

            // Создаем текстовое поле для ввода HEX
            const hexInput = document.createElement('input');
            hexInput.type = 'text';
            hexInput.className = 'color-picker-hex-input';
            hexInput.value = picker.value || '#000000';
            hexInput.maxLength = 7;
            hexInput.style.cssText = `
                width: 100%;
                padding: 10px 12px;
                font-size: 14px;
                font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
                border: 2px solid #ddd;
                border-radius: 6px;
                margin-bottom: 8px;
                box-sizing: border-box;
                transition: border-color 0.3s;
            `;

            // Создаем метку для отображения названия цвета (если возможно)
            const colorNameLabel = document.createElement('div');
            colorNameLabel.className = 'color-picker-name';
            colorNameLabel.style.cssText = `
                font-size: 12px;
                color: #666;
                margin-top: 5px;
                font-style: italic;
            `;

            // Определяем название цвета по HEX (основные цвета)
            function getColorName(hex) {
                const colors = {
                    '#3b82f6': 'Синий (Primary)',
                    '#8b5cf6': 'Фиолетовый (Secondary)',
                    '#10b981': 'Зеленый (Accent)',
                    '#1f2937': 'Темно-серый (Text)',
                    '#f9fafb': 'Светло-серый (Background)',
                    '#ffffff': 'Белый (Header)',
                    '#111827': 'Темно-серый (Footer)',
                    '#000000': 'Черный',
                    '#ffffff': 'Белый',
                    '#ff0000': 'Красный',
                    '#00ff00': 'Зеленый',
                    '#0000ff': 'Синий',
                    '#ffff00': 'Желтый',
                    '#ff00ff': 'Пурпурный',
                    '#00ffff': 'Голубой'
                };

                return colors[hex.toLowerCase()] || 'Пользовательский цвет';
            }

            // Обновляем название цвета
            function updateColorName() {
                colorNameLabel.textContent = getColorName(picker.value);
            }

            // Создаем блок предварительного просмотра применения цвета
            const previewContainer = document.createElement('div');
            previewContainer.style.cssText = `
                margin-top: 10px;
                padding: 10px;
                background: white;
                border-radius: 6px;
                border: 1px solid #eee;
                display: flex;
                gap: 10px;
                flex-wrap: wrap;
            `;

            // Создаем примеры применения цвета
            function createColorPreview() {
                previewContainer.innerHTML = '';

                const examples = [
                    { label: 'Текст', style: `color: ${picker.value}; font-weight: bold;` },
                    { label: 'Фон', style: `background-color: ${picker.value}; color: white; padding: 5px 10px; border-radius: 4px;` },
                    { label: 'Кнопка', style: `background-color: ${picker.value}; color: white; padding: 6px 12px; border-radius: 6px; border: none; font-weight: bold;` },
                    { label: 'Граница', style: `border: 2px solid ${picker.value}; padding: 5px 10px; border-radius: 4px;` }
                ];

                examples.forEach(example => {
                    const exampleElement = document.createElement('div');
                    exampleElement.style.cssText = `
                        display: flex;
                        flex-direction: column;
                        align-items: center;
                        gap: 5px;
                        font-size: 11px;
                    `;

                    const previewElement = document.createElement('div');
                    previewElement.textContent = example.label;
                    previewElement.style.cssText = example.style + 'min-width: 60px; text-align: center;';

                    exampleElement.appendChild(previewElement);
                    previewContainer.appendChild(exampleElement);
                });
            }

            // Функция для затемнения цвета (для границы)
            function darkenColor(hex, percent) {
                hex = hex.replace('#', '');

                let r = parseInt(hex.substring(0, 2), 16);
                let g = parseInt(hex.substring(2, 4), 16);
                let b = parseInt(hex.substring(4, 6), 16);

                r = Math.floor(r * (1 - percent));
                g = Math.floor(g * (1 - percent));
                b = Math.floor(b * (1 - percent));

                return `#${r.toString(16).padStart(2, '0')}${g.toString(16).padStart(2, '0')}${b.toString(16).padStart(2, '0')}`;
            }

            // Обновление визуального представления
            function updateVisuals() {
                const colorValue = picker.value;

                // Обновляем кнопку
                colorButton.style.backgroundColor = colorValue;
                colorButton.style.borderColor = darkenColor(colorValue, 0.2);

                // Обновляем текстовое поле
                hexInput.value = colorValue;

                // Обновляем цвет текстового поля (контрастный)
                const textColor = getContrastColor(colorValue);
                hexInput.style.color = textColor;
                hexInput.style.backgroundColor = colorValue;
                hexInput.style.borderColor = darkenColor(colorValue, 0.3);

                // Обновляем название
                updateColorName();

                // Обновляем превью
                createColorPreview();
            }

            // Получение контрастного цвета (черный или белый)
            function getContrastColor(hex) {
                hex = hex.replace('#', '');

                const r = parseInt(hex.substring(0, 2), 16);
                const g = parseInt(hex.substring(2, 4), 16);
                const b = parseInt(hex.substring(4, 6), 16);

                // Яркость по формуле
                const brightness = (r * 299 + g * 587 + b * 114) / 1000;

                return brightness > 128 ? '#000000' : '#ffffff';
            }

            // Обработчик изменения цвета в нативном пикере
            picker.addEventListener('input', function() {
                updateVisuals();
            });

            // Обработчик изменения в текстовом поле
            hexInput.addEventListener('input', function() {
                let value = this.value;

                // Добавляем # если его нет
                if (value && !value.startsWith('#')) {
                    value = '#' + value;
                    this.value = value;
                }

                // Проверяем корректность HEX кода
                if (/^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$/.test(value)) {
                    // Если короткий формат (#RGB), преобразуем в полный (#RRGGBB)
                    if (value.length === 4) {
                        value = '#' + value[1] + value[1] + value[2] + value[2] + value[3] + value[3];
                    }

                    picker.value = value;
                    updateVisuals();
                }
            });

            // Подсказка при фокусе
            hexInput.addEventListener('focus', function() {
                this.style.outline = 'none';
                this.style.borderColor = '#3b82f6';
                this.style.boxShadow = '0 0 0 2px rgba(59, 130, 246, 0.2)';
            });

            hexInput.addEventListener('blur', function() {
                this.style.boxShadow = 'none';
            });

            // Вставляем все элементы в контейнер
            infoContainer.appendChild(hexInput);
            infoContainer.appendChild(colorNameLabel);
            infoContainer.appendChild(previewContainer);

            pickerContainer.appendChild(colorButton);
            pickerContainer.appendChild(infoContainer);

            // Вставляем контейнер после оригинального поля и скрываем оригинальный input
            fieldContainer.appendChild(pickerContainer);
            picker.style.position = 'absolute';
            picker.style.opacity = '0';
            picker.style.width = '60px';
            picker.style.height = '60px';
            picker.style.pointerEvents = 'none';

            // Инициализация визуалов
            updateVisuals();
        });
    }

    // Инициализация при загрузке
    initializeColorPickers();

    // Также инициализируем при динамическом добавлении полей (если есть)
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            if (mutation.addedNodes.length) {
                initializeColorPickers();
            }
        });
    });

    // Начинаем наблюдение за изменениями в DOM
    observer.observe(document.body, {
        childList: true,
        subtree: true
    });

    // Добавляем глобальную функцию для ручной инициализации
    window.initializeColorPickers = initializeColorPickers;
});
