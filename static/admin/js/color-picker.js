// static/admin/js/color-picker.js

document.addEventListener('DOMContentLoaded', function() {
    // Функция для инициализации всех цветовых пикеров на странице
    function initializeColorPickers() {
        // Находим все контейнеры цветовых пикеров
        const colorPickers = document.querySelectorAll('.color-picker-widget');

        colorPickers.forEach(function(pickerContainer) {
            const colorInput = pickerContainer.querySelector('input[type="color"]');
            const hexInput = pickerContainer.querySelector('.color-hex-input');

            if (!colorInput || !hexInput) return;

            // Обновляем текстовое поле при изменении цвета
            function updateFromColorInput() {
                const colorValue = colorInput.value;
                hexInput.value = colorValue;
                // Также обновляем border цвета, чтобы показать текущий цвет
                colorInput.style.borderColor = adjustBrightness(colorValue, -0.3);
            }

            // Обновляем цветовой пикер при изменении текстового поля
            function updateFromHexInput() {
                let value = hexInput.value;

                // Добавляем # если его нет
                if (value && !value.startsWith('#')) {
                    value = '#' + value;
                    hexInput.value = value;
                }

                // Проверяем корректность HEX кода
                if (/^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$/.test(value)) {
                    // Если короткий формат (#RGB), преобразуем в полный (#RRGGBB)
                    if (value.length === 4) {
                        value = '#' + value[1] + value[1] + value[2] + value[2] + value[3] + value[3];
                        hexInput.value = value;
                    }

                    colorInput.value = value;
                    colorInput.style.borderColor = adjustBrightness(value, -0.3);
                }
            }

            // Функция для регулировки яркости цвета (для границы)
            function adjustBrightness(hex, percent) {
                hex = hex.replace('#', '');

                let r = parseInt(hex.substring(0, 2), 16);
                let g = parseInt(hex.substring(2, 4), 16);
                let b = parseInt(hex.substring(4, 6), 16);

                r = Math.min(255, Math.max(0, r + r * percent));
                g = Math.min(255, Math.max(0, g + g * percent));
                b = Math.min(255, Math.max(0, b + b * percent));

                return `#${Math.round(r).toString(16).padStart(2, '0')}${Math.round(g).toString(16).padStart(2, '0')}${Math.round(b).toString(16).padStart(2, '0')}`;
            }

            // Связываем события
            colorInput.addEventListener('input', updateFromColorInput);
            hexInput.addEventListener('input', updateFromHexInput);
            hexInput.addEventListener('blur', updateFromHexInput);

            // Устанавливаем стиль для цветового пикера
            colorInput.style.width = '50px';
            colorInput.style.height = '50px';
            colorInput.style.borderRadius = '4px';
            colorInput.style.border = '2px solid';
            colorInput.style.cursor = 'pointer';

            // Инициализируем начальное состояние
            updateFromColorInput();
        });
    }

    // Инициализация при загрузке страницы
    initializeColorPickers();

    // Также инициализируем при динамическом добавлении полей
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            if (mutation.addedNodes.length) {
                initializeColorPickers();
            }
        });
    });

    observer.observe(document.body, {
        childList: true,
        subtree: true
    });
});
