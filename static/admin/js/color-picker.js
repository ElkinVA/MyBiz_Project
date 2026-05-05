// static/admin/js/color-picker.js
// Надёжный синхронизатор цветовых пикеров и HEX-полей

document.addEventListener('DOMContentLoaded', function () {
    'use strict';

    /**
     * Инициализация одного виджета
     * @param {HTMLElement} widget - элемент с классом .color-picker-widget
     */
    function initColorPicker(widget) {
        // Защита от повторной инициализации
        if (widget.dataset.colorPickerInitialized === 'true') return;

        const colorInput = widget.querySelector('input[type="color"]');
        const hexInput = widget.querySelector('.color-hex-input');

        // Если нет необходимых элементов — ничего не делаем
        if (!colorInput || !hexInput) return;

        // Вспомогательные функции для обновления
        function updateFromColor() {
            hexInput.value = colorInput.value;
        }

        function normalizeHex(val) {
            let hex = val.trim();
            if (hex && !hex.startsWith('#')) hex = '#' + hex;
            hex = hex.toLowerCase();
            if (/^#([0-9a-f]{6}|[0-9a-f]{3})$/.test(hex)) {
                if (hex.length === 4) {
                    hex = '#' + hex[1] + hex[1] + hex[2] + hex[2] + hex[3] + hex[3];
                }
                return hex;
            }
            return null;
        }

        function updateFromHex() {
            const normalized = normalizeHex(hexInput.value);
            if (normalized) {
                hexInput.value = normalized;
                colorInput.value = normalized;
            }
        }

        // Обработчики событий
        colorInput.addEventListener('input', updateFromColor);
        hexInput.addEventListener('input', debounce(updateFromHex, 300));
        hexInput.addEventListener('blur', updateFromHex);

        // Сразу синхронизируем начальное состояние
        if (colorInput.value) {
            updateFromColor();
        } else if (hexInput.value) {
            const normalized = normalizeHex(hexInput.value);
            if (normalized) {
                colorInput.value = normalized;
                hexInput.value = normalized;
            } else {
                // Если HEX некорректен — ставим чёрный по умолчанию
                colorInput.value = '#000000';
                hexInput.value = '#000000';
            }
        } else {
            // Оба пустые — выставляем дефолтный чёрный
            colorInput.value = '#000000';
            hexInput.value = '#000000';
        }

        widget.dataset.colorPickerInitialized = 'true';
    }

    /**
     * Инициализация всех виджетов на странице
     */
    function initAllColorPickers() {
        document.querySelectorAll('.color-picker-widget').forEach(initColorPicker);
    }

    // Первичная инициализация
    initAllColorPickers();

    // Наблюдатель за динамическими изменениями (например, при открытии collapsed fieldsets)
    new MutationObserver(function () {
        initAllColorPickers();
    }).observe(document.body, {
        childList: true,
        subtree: true
    });

    // Простая реализация debounce
    function debounce(fn, delay) {
        let timeout;
        return function (...args) {
            clearTimeout(timeout);
            timeout = setTimeout(() => fn.apply(this, args), delay);
        };
    }
});
