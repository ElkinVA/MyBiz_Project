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
        initAutoSave();
        initKeyboardShortcuts();
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
     * Автосохранение форм
     */
    function initAutoSave() {
        const form = document.querySelector('#content-main form');
        if (!form) return;

        const formInputs = form.querySelectorAll('input, textarea, select');
        const formId = form.id || 'admin_form';

        // Загрузка сохранённых данных
        formInputs.forEach(function(input) {
            const inputName = input.name;
            if (inputName) {
                const savedValue = localStorage.getItem('autosave_' + formId + '_' + inputName);
                if (savedValue && input.type !== 'hidden') {
                    if (input.type === 'checkbox') {
                        input.checked = savedValue === 'true';
                    } else {
                        input.value = savedValue;
                    }
                }
            }
        });

        // Сохранение при изменении
        formInputs.forEach(function(input) {
            input.addEventListener('change', function() {
                const inputName = input.name;
                if (inputName) {
                    const value = input.type === 'checkbox' ? input.checked : input.value;
                    localStorage.setItem('autosave_' + formId + '_' + inputName, value);

                    // Показать уведомление
                    showAutoSaveNotification();
                }
            });
        });

        // Очистка при отправке
        form.addEventListener('submit', function() {
            formInputs.forEach(function(input) {
                const inputName = input.name;
                if (inputName) {
                    localStorage.removeItem('autosave_' + formId + '_' + inputName);
                }
            });
        });
    }

    /**
     * Уведомление об автосохранении
     */
    function showAutoSaveNotification() {
        const existingNotification = document.querySelector('.autosave-notification');
        if (existingNotification) {
            existingNotification.remove();
        }

        const notification = document.createElement('div');
        notification.className = 'autosave-notification';
        notification.textContent = '✓ Изменения сохранены автоматически';
        notification.style.cssText = `
            position: fixed;
            bottom: 20px;
            right: 20px;
            background: linear-gradient(135deg, #10b981, #059669);
            color: white;
            padding: 12px 20px;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
            z-index: 10000;
            animation: slideIn 0.3s ease;
        `;

        document.body.appendChild(notification);

        setTimeout(function() {
            notification.style.animation = 'slideOut 0.3s ease';
            setTimeout(function() {
                notification.remove();
            }, 300);
        }, 2000);
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
    `;
    document.head.appendChild(style);

})();
