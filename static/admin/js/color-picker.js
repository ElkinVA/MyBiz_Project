// static/admin/js/color-picker.js
// Синхронизация цветовых пикеров

document.addEventListener('DOMContentLoaded', function() {
    // Инициализация всех пикеров на странице
    initializeColorPickers();

    // Наблюдатель за динамическими элементами
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

    // Отключаем observer при выгрузке страницы
    window.addEventListener('beforeunload', function() {
        observer.disconnect();
    });
});

function initializeColorPickers() {
    const colorPickers = document.querySelectorAll('.color-picker-widget');

    colorPickers.forEach(function(pickerContainer) {
        // Проверяем, не инициализирован ли уже этот пикер
        if (pickerContainer.dataset.initialized === 'true') return;

        const colorInput = pickerContainer.querySelector('input[type="color"]');
        const hexInput = pickerContainer.querySelector('.color-hex-input');

        if (!colorInput || !hexInput) return;

        // Функция обновления из цветового пикера
        function updateFromColorInput() {
            const colorValue = colorInput.value;
            hexInput.value = colorValue;
            // Небольшое изменение границы для визуального отклика
            colorInput.style.borderColor = adjustBrightness(colorValue, -0.3);
        }

        // Функция обновления из HEX-поля с debounce
        const updateFromHexInput = debounce(function() {
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
        }, 300);

        // Функция для регулировки яркости цвета (с защитой от ошибок)
        function adjustBrightness(hex, percent) {
            try {
                // Приводим к 6-символьному виду
                let cleanHex = hex.replace('#', '');
                if (cleanHex.length === 3) {
                    cleanHex = cleanHex.split('').map(c => c + c).join('');
                }
                if (cleanHex.length !== 6) {
                    return hex; // невалидный HEX, возвращаем как есть
                }

                let r = parseInt(cleanHex.substring(0, 2), 16);
                let g = parseInt(cleanHex.substring(2, 4), 16);
                let b = parseInt(cleanHex.substring(4, 6), 16);

                r = Math.min(255, Math.max(0, Math.round(r + r * percent)));
                g = Math.min(255, Math.max(0, Math.round(g + g * percent)));
                b = Math.min(255, Math.max(0, Math.round(b + b * percent)));

                return `#${r.toString(16).padStart(2, '0')}${g.toString(16).padStart(2, '0')}${b.toString(16).padStart(2, '0')}`;
            } catch (e) {
                console.warn('Error adjusting brightness:', e);
                return hex;
            }
        }

        // Функция debounce
        function debounce(func, wait) {
            let timeout;
            return function(...args) {
                clearTimeout(timeout);
                timeout = setTimeout(() => func.apply(this, args), wait);
            };
        }

        // Связываем события
        colorInput.addEventListener('input', updateFromColorInput);
        hexInput.addEventListener('input', updateFromHexInput);
        hexInput.addEventListener('blur', updateFromHexInput);

        // Инициализируем начальное состояние
        updateFromColorInput();

        // Помечаем как инициализированный
        pickerContainer.dataset.initialized = 'true';
    });
}
