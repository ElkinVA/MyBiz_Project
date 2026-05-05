/**
 * MyBiz Admin Enhanced JavaScript
 * Улучшения для админ-панели Django
 */

(function() {
    'use strict';

    // Инициализация после загрузки DOM
    document.addEventListener('DOMContentLoaded', function() {
        initEnhancedAdmin();
    });

    /**
     * Основная функция инициализации
     */
    function initEnhancedAdmin() {
        initFieldsetCollapse();
        initSearchEnhancements();
        initActionCheckboxes();
        initDateTimeWidgets();
        initKeyboardShortcuts();
        initUnsavedChangesWarning();
        initScrollToErrors();
    }

    /**
     * Улучшение сворачивания fieldset
     */
    function initFieldsetCollapse() {
        const collapseElements = document.querySelectorAll('fieldset.collapse');

        collapseElements.forEach(function(fieldset) {
            const h2 = fieldset.querySelector('h2');
            if (h2) {
                h2.style.cursor = 'pointer';
                h2.addEventListener('click', function() {
                    fieldset.classList.toggle('collapsed');

                    // Сохранение состояния в localStorage
                    const fieldsetId = fieldset.id || fieldset.querySelector('h2').textContent;
                    localStorage.setItem('fieldset_' + fieldsetId, fieldset.classList.contains('collapsed'));
                });

                // Восстановление состояния
                const fieldsetId = fieldset.id || fieldset.querySelector('h2').textContent;
                const isCollapsed = localStorage.getItem('fieldset_' + fieldsetId);
                if (isCollapsed === 'true') {
                    fieldset.classList.add('collapsed');
                }
            }
        });
    }

    /**
     * Улучшение поиска
     */
    function initSearchEnhancements() {
        const searchForm = document.querySelector('#changelist-search form');
        const searchInput = document.querySelector('#changelist-search input[type="text"]');

        if (searchInput) {
            // Автофокус при загрузке
            searchInput.focus();

            // Поиск по Ctrl+Enter
            searchInput.addEventListener('keydown', function(e) {
                if (e.ctrlKey && e.key === 'Enter') {
                    searchForm.submit();
                }
            });

            // Очистка по Esc
            searchInput.addEventListener('keydown', function(e) {
                if (e.key === 'Escape') {
                    searchInput.value = '';
                    searchInput.focus();
                }
            });
        }
    }

    /**
     * Улучшение чекбоксов действий
     */
    function initActionCheckboxes() {
        const selectAllCheckbox = document.querySelector('#action-toggle');
        const actionCheckboxes = document.querySelectorAll('.action-select');

        if (selectAllCheckbox) {
            selectAllCheckbox.addEventListener('change', function() {
                const isChecked = this.checked;
                actionCheckboxes.forEach(function(checkbox) {
                    checkbox.checked = isChecked;
                    highlightSelectedRow(checkbox, isChecked);
                });
            });
        }

        actionCheckboxes.forEach(function(checkbox) {
            checkbox.addEventListener('change', function() {
                highlightSelectedRow(this, this.checked);
                updateSelectAllState();
            });

            // Подсветка строки
            const row = checkbox.closest('tr');
            if (row) {
                row.style.cursor = 'pointer';
                row.addEventListener('click', function(e) {
                    if (e.target.tagName !== 'A' && e.target.tagName !== 'INPUT') {
                        checkbox.checked = !checkbox.checked;
                        highlightSelectedRow(checkbox, checkbox.checked);
                        updateSelectAllState();
                    }
                });
            }
        });
    }

    /**
     * Подсветка выбранной строки
     */
    function highlightSelectedRow(checkbox, isSelected) {
        const row = checkbox.closest('tr');
        if (row) {
            if (isSelected) {
                row.style.backgroundColor = 'rgba(59, 130, 246, 0.1)';
            } else {
                row.style.backgroundColor = '';
            }
        }
    }

    /**
     * Обновление состояния "Выбрать все"
     */
    function updateSelectAllState() {
        const selectAllCheckbox = document.querySelector('#action-toggle');
        const actionCheckboxes = document.querySelectorAll('.action-select');
        const checkedCount = document.querySelectorAll('.action-select:checked').length;

        if (selectAllCheckbox && actionCheckboxes.length > 0) {
            selectAllCheckbox.checked = checkedCount === actionCheckboxes.length;
            selectAllCheckbox.indeterminate = checkedCount > 0 && checkedCount < actionCheckboxes.length;
        }
    }

    /**
     * Улучшение виджетов даты и времени
     */
    function initDateTimeWidgets() {
        const dateInputs = document.querySelectorAll('input[type="text"][name*="date"]');
        const timeInputs = document.querySelectorAll('input[type="text"][name*="time"]');

        dateInputs.forEach(function(input) {
            input.placeholder = 'ДД.ММ.ГГГГ';
        });

        timeInputs.forEach(function(input) {
            input.placeholder = 'ЧЧ:ММ';
        });
    }

    /**
     * Горячие клавиши
     */
    function initKeyboardShortcuts() {
        document.addEventListener('keydown', function(e) {
            // Ctrl+S - Сохранить
            if (e.ctrlKey && e.key === 's') {
                e.preventDefault();
                const saveButton = document.querySelector('.submit-row input[type="submit"]');
                if (saveButton) {
                    saveButton.click();
                }
            }

            // Ctrl+D - Удалить
            if (e.ctrlKey && e.key === 'd') {
                e.preventDefault();
                const deleteButton = document.querySelector('.submit-row a.deletelink');
                if (deleteButton) {
                    deleteButton.click();
                }
            }

            // Ctrl+F - Фокус на поиск
            if (e.ctrlKey && e.key === 'f') {
                e.preventDefault();
                const searchInput = document.querySelector('#changelist-search input[type="text"]');
                if (searchInput) {
                    searchInput.focus();
                }
            }

            // Escape - Закрыть модальные окна
            if (e.key === 'Escape') {
                const modal = document.querySelector('.related-popup');
                if (modal) {
                    modal.querySelector('.popup-close')?.click();
                }
            }
        });
    }

    /**
     * Предупреждение о несохранённых изменениях
     * Работает для всех форм редактирования в админке
     */
    function initUnsavedChangesWarning() {
        // Проверяем, что мы на странице изменения объекта (не список)
        const changeForm = document.querySelector('#content-main form');
        if (!changeForm) {
            return;
        }

        // Флаг для отслеживания изменений
        let hasUnsavedChanges = false;
        // Флаг отправки формы
        let isSubmitting = false;

        // Получаем все поля ввода кроме скрытых и кнопок
        const formInputs = changeForm.querySelectorAll('input:not([type="hidden"]):not([type="submit"]):not([type="button"]), textarea, select');

        // Добавляем обработчики изменений
        formInputs.forEach(function(input) {
            input.addEventListener('change', function() {
                hasUnsavedChanges = true;
            });
            input.addEventListener('input', function() {
                hasUnsavedChanges = true;
            });
        });

        // Предупреждение при попытке уйти с страницы с несохранёнными изменениями
        window.addEventListener('beforeunload', function(e) {
            if (hasUnsavedChanges && !isSubmitting) {
                e.preventDefault();
                e.returnValue = '';
                return '';
            }
        });

        // После успешной отправки формы сбрасываем флаг
        changeForm.addEventListener('submit', function() {
            isSubmitting = true;
            hasUnsavedChanges = false;
        });
    }

    /**
     * Автоматическая прокрутка к ошибкам валидации
     * Если на странице есть ошибки, прокручиваем к первой ошибке
     */
    function initScrollToErrors() {
        // Ищем элементы с ошибками
        const errorNote = document.querySelector('.errornote');
        const errorList = document.querySelector('.errorlist');
        const formRowError = document.querySelector('.form-row.errors');

        // Приоритет: errornote -> errorlist -> form-row с ошибками
        const errorElement = errorNote || errorList || formRowError;

        if (errorElement) {
            // Плавная прокрутка к ошибке
            errorElement.scrollIntoView({
                behavior: 'smooth',
                block: 'center'
            });

            // Дополнительно добавляем визуальный акцент
            errorElement.style.animation = 'highlightError 0.5s ease-in-out';
        }
    }

    /**
     * Добавление анимаций
     */
    const style = document.createElement('style');
    style.textContent = `
        @keyframes slideIn {
            from {
                transform: translateX(100%);
                opacity: 0;
            }
            to {
                transform: translateX(0);
                opacity: 1;
            }
        }

        @keyframes slideOut {
            from {
                transform: translateX(0);
                opacity: 1;
            }
            to {
                transform: translateX(100%);
                opacity: 0;
            }
        }

        @keyframes highlightError {
            0%, 100% {
                background-color: transparent;
            }
            50% {
                background-color: rgba(239, 68, 68, 0.1);
            }
        }
    `;
    document.head.appendChild(style);

})();
