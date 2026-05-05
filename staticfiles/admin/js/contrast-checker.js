// static/admin/js/contrast-checker.js
// Проверка контрастности цветов для доступности (WCAG 2.1)
// Автоматическая валидация сочетаний цветов текста и фона

document.addEventListener('DOMContentLoaded', function() {
    console.log('>>> Contrast checker загружен');
    
    // Пары полей для проверки контрастности
    const contrastPairs = [
        {
            bgField: 'header_bg_color',
            textField: 'header_text_color',
            containerId: 'header-contrast-indicator',
            label: 'Шапка (Header)'
        },
        {
            bgField: 'footer_bg_color',
            textField: 'footer_text_color',
            containerId: 'footer-contrast-indicator',
            label: 'Подвал (Footer)'
        },
        {
            bgField: 'hero_bg_color',
            textField: 'text_color',
            containerId: 'hero-contrast-indicator',
            label: 'Hero-секция'
        },
        {
            bgField: 'background_color',
            textField: 'text_color',
            containerId: 'body-contrast-indicator',
            label: 'Основной контент'
        }
    ];

    // Инициализация индикаторов контрастности
    function initContrastIndicators() {
        contrastPairs.forEach(pair => {
            const bgInput = document.querySelector(`input[name="${pair.bgField}"]`);
            const textInput = document.querySelector(`input[name="${pair.textField}"]`);
            
            if (!bgInput || !textInput) return;

            // Создаём индикатор, если ещё не создан
            let indicator = document.getElementById(pair.containerId);
            if (!indicator) {
                indicator = createContrastIndicator(pair);
                // Вставляем индикатор после поля фона (background_color или hero_bg_color или footer_bg_color)
                const bgFormRow = bgInput.closest('.form-row');
                if (bgFormRow) {
                    bgFormRow.after(indicator);
                }
            }

            // Добавляем обработчики изменений
            bgInput.addEventListener('input', () => checkContrast(pair));
            textInput.addEventListener('input', () => checkContrast(pair));
            
            // Первичная проверка
            setTimeout(() => checkContrast(pair), 500);
        });
        
        // Добавляем clearfix после последнего индикатора в каждой группе
        addContrastClearfix();
    }
    
    // Добавление clearfix для очистки float после индикаторов
    function addContrastClearfix() {
        // Находим все группы полей и добавляем clearfix после последней пары в группе
        const clearFields = ['border_color', 'hero_bg_color', 'footer_text_color'];
        clearFields.forEach(fieldName => {
            const field = document.querySelector(`input[name="${fieldName}"]`);
            if (field) {
                const formRow = field.closest('.form-row');
                if (formRow && !formRow.nextElementSibling?.classList.contains('clearfix-contrast')) {
                    const clearfix = document.createElement('div');
                    clearfix.className = 'clearfix-contrast';
                    formRow.after(clearfix);
                }
            }
        });
    }

    // Создание HTML индикатора
    function createContrastIndicator(pair) {
        const div = document.createElement('div');
        div.id = pair.containerId;
        div.className = 'contrast-indicator';
        div.innerHTML = `
            <div class="contrast-label">${pair.label}</div>
            <div class="contrast-info-icon" data-wcag-info="WCAG — международный стандарт доступности. Он показывает коэффициент контрастности и уровни (AA, AAA), чтобы цвета вашего оформления хорошо различали люди. Чем выше контраст, тем легче читать текст и пользоваться сайтом.">ℹ️</div>
            <div class="contrast-ratio">
                <span class="ratio-value">--</span>
                <span class="ratio-status"></span>
            </div>
            <div class="contrast-preview">
                <div class="preview-box">
                    <span class="preview-text">Aa</span>
                </div>
            </div>
            <div class="contrast-message"></div>
        `;
        return div;
    }

    // Проверка контрастности для пары
    function checkContrast(pair) {
        const bgInput = document.querySelector(`input[name="${pair.bgField}"]`);
        const textInput = document.querySelector(`input[name="${pair.textField}"]`);
        const indicator = document.getElementById(pair.containerId);
        
        if (!bgInput || !textInput || !indicator) return;

        const bgColor = bgInput.value;
        const textColor = textInput.value;

        const ratio = calculateContrastRatio(bgColor, textColor);
        const aaNormal = 4.5;
        const aaLarge = 3.0;
        const aaaNormal = 7.0;
        const aaaLarge = 4.5;

        const ratioValue = indicator.querySelector('.ratio-value');
        const ratioStatus = indicator.querySelector('.ratio-status');
        const message = indicator.querySelector('.contrast-message');
        const previewBox = indicator.querySelector('.preview-box');
        const previewText = indicator.querySelector('.preview-text');

        // Обновляем значение коэффициента
        ratioValue.textContent = ratio.toFixed(2) + ':1';

        // Определяем статус и сообщение
        let status, statusClass, msg;
        
        if (ratio >= aaaNormal) {
            status = 'AAA';
            statusClass = 'excellent';
            msg = '✅ Отлично! Соответствует WCAG AAA (любой текст)';
        } else if (ratio >= aaNormal) {
            status = 'AA';
            statusClass = 'good';
            msg = '✅ Хорошо! Соответствует WCAG AA (обычный текст)';
        } else if (ratio >= aaLarge) {
            status = 'AA Large';
            statusClass = 'warning';
            msg = '⚠️ Допустимо только для крупного текста (18px+ или 14px bold)';
        } else {
            status = 'Fail';
            statusClass = 'error';
            msg = '❌ Плохо! Недостаточный контраст для доступности';
        }

        ratioStatus.textContent = status;
        ratioStatus.className = `ratio-status ${statusClass}`;
        message.textContent = msg;
        message.className = `contrast-message ${statusClass}`;

        // Обновляем превью
        previewBox.style.backgroundColor = bgColor;
        previewText.style.color = textColor;
        
        // Добавляем класс статуса к индикатору
        indicator.className = `contrast-indicator ${statusClass}`;
    }

    // Расчёт коэффициента контрастности (WCAG 2.1)
    function calculateContrastRatio(color1, color2) {
        const lum1 = getLuminance(hexToRgb(color1));
        const lum2 = getLuminance(hexToRgb(color2));
        
        const lighter = Math.max(lum1, lum2);
        const darker = Math.min(lum1, lum2);
        
        return (lighter + 0.05) / (darker + 0.05);
    }

    // Расчёт относительной яркости (WCAG формула)
    function getLuminance(rgb) {
        const [r, g, b] = [rgb.r, rgb.g, rgb.b].map(c => {
            c = c / 255;
            return c <= 0.03928 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4);
        });
        return 0.2126 * r + 0.7152 * g + 0.0722 * b;
    }

    // Конвертация HEX в RGB
    function hexToRgb(hex) {
        hex = hex.replace('#', '');
        
        // Поддержка 3-значных HEX
        if (hex.length === 3) {
            hex = hex.split('').map(c => c + c).join('');
        }
        
        const bigint = parseInt(hex, 16);
        return {
            r: (bigint >> 16) & 255,
            g: (bigint >> 8) & 255,
            b: bigint & 255
        };
    }

    // Запуск после небольшой задержки (для загрузки всех полей)
    setTimeout(initContrastIndicators, 800);
});
