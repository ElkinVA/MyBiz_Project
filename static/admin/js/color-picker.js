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
            // Обновляем превью цвета
            const preview = pickerContainer.querySelector('.color-preview');
            if (preview) {
                preview.style.backgroundColor = colorValue;
            }
        }

        // Функция обновления из HEX-поля
        const updateFromHexInput = debounce(function() {
            let value = hexInput.value.trim();

            // Добавляем # если его нет
            if (value && !value.startsWith('#')) {
                value = '#' + value;
            }

            // Преобразуем к нижнему регистру
            value = value.toLowerCase();

            // Проверяем корректность HEX кода
            if (/^#([a-f0-9]{6}|[a-f0-9]{3})$/.test(value)) {
                // Если короткий формат (#RGB), преобразуем в полный (#RRGGBB)
                if (value.length === 4) {
                    value = '#' + value[1] + value[1] + value[2] + value[2] + value[3] + value[3];
                }
                hexInput.value = value;
                colorInput.value = value;
                // Обновляем превью цвета
                const preview = pickerContainer.querySelector('.color-preview');
                if (preview) {
                    preview.style.backgroundColor = value;
                }
            }
        }, 300);

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
