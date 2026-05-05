/**
 * sitesettings_save_sections.js
 * Скрипт для добавления кнопок "Сохранить" в каждый раздел формы SiteSettings
 * и сохранения состояния сворачивания/разворачивания разделов
 */

(function() {
    'use strict';

    const STORAGE_KEY = 'siteSettings_fieldsets_state';

    /**
     * Сохраняет состояние всех fieldset в localStorage
     */
    function saveFieldsetsState() {
        const fieldsets = document.querySelectorAll('fieldset.module');
        const state = {};
        
        fieldsets.forEach(function(fieldset, index) {
            const id = fieldset.id || 'fieldset_' + index;
            // Проверяем, свернут ли fieldset (через details[open] или класс collapsed)
            const details = fieldset.querySelector('details');
            if (details) {
                state[id] = details.hasAttribute('open');
            } else {
                state[id] = !fieldset.classList.contains('collapsed');
            }
        });
        
        try {
            localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
        } catch (e) {
            console.warn('Не удалось сохранить состояние разделов:', e);
        }
    }

    /**
     * Восстанавливает состояние fieldset из localStorage
     */
    function restoreFieldsetsState() {
        try {
            const saved = localStorage.getItem(STORAGE_KEY);
            if (!saved) return;
            
            const state = JSON.parse(saved);
            const fieldsets = document.querySelectorAll('fieldset.module');
            
            fieldsets.forEach(function(fieldset) {
                const id = fieldset.id || 'fieldset_' + Array.prototype.indexOf.call(fieldsets, fieldset);
                if (state.hasOwnProperty(id)) {
                    const details = fieldset.querySelector('details');
                    if (details) {
                        // Для details: open=true если развернут
                        if (state[id]) {
                            details.setAttribute('open', 'open');
                        } else {
                            details.removeAttribute('open');
                        }
                    } else {
                        // Для старых fieldset с классом collapsed
                        if (state[id]) {
                            fieldset.classList.remove('collapsed');
                        } else {
                            fieldset.classList.add('collapsed');
                        }
                    }
                }
            });
        } catch (e) {
            console.warn('Не удалось восстановить состояние разделов:', e);
        }
    }

    /**
     * Добавляет кнопку "Сохранить" в каждый fieldset
     */
    function addSaveButtonsToFieldsets() {
        const fieldsets = document.querySelectorAll('fieldset.module');
        
        fieldsets.forEach(function(fieldset) {
            // Проверяем, есть ли уже кнопка
            if (fieldset.querySelector('.section-save-btn')) {
                return;
            }
            
            // Находим summary (для collapsible fieldset) или заголовок
            let insertTarget = fieldset.querySelector('summary');
            
            // Если нет summary, пробуем найти заголовок
            if (!insertTarget) {
                insertTarget = fieldset.querySelector('h2.fieldset-heading');
            }
            if (!insertTarget) {
                insertTarget = fieldset.querySelector('legend');
            }
            if (!insertTarget) return;
            
            // Создаём кнопку
            const saveBtn = document.createElement('button');
            saveBtn.type = 'button';
            saveBtn.className = 'section-save-btn default';
            saveBtn.textContent = '💾 Сохранить';
            saveBtn.style.cssText = 'float: right; margin-left: auto; padding: 4px 10px; font-size: 0.85rem; height: auto; line-height: normal; cursor: pointer;';
            
            // Обработчик клика
            saveBtn.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();
                
                // Сохраняем состояние перед отправкой
                saveFieldsetsState();
                
                // Находим форму и отправляем её с параметром _save
                const form = document.querySelector('form');
                if (!form) return;
                
                // Удаляем параметр _continue если он есть
                const continueInput = form.querySelector('input[name="_continue"]');
                if (continueInput) {
                    continueInput.remove();
                }
                
                // Добавляем параметр _save
                let saveInput = form.querySelector('input[name="_save"]');
                if (!saveInput) {
                    saveInput = document.createElement('input');
                    saveInput.type = 'hidden';
                    saveInput.name = '_save';
                    saveInput.value = '1';
                    form.appendChild(saveInput);
                }
                
                // Отправляем форму
                form.submit();
            });
            
            // Вставляем кнопку в конец summary/заголовка
            insertTarget.appendChild(saveBtn);
            
            // Также отслеживаем клик по summary/details для обновления состояния
            const detailsElement = fieldset.querySelector('details');
            if (detailsElement) {
                detailsElement.addEventListener('toggle', function() {
                    // Небольшая задержка чтобы атрибут open успел примениться
                    setTimeout(saveFieldsetsState, 50);
                });
            }
            
            // И отслеживаем клик по заголовку
            insertTarget.addEventListener('click', function(e) {
                setTimeout(saveFieldsetsState, 100);
            });
        });
    }

    /**
     * Инициализация после загрузки DOM
     */
    function init() {
        // Восстанавливаем состояние разделов
        restoreFieldsetsState();
        
        // Добавляем кнопки сохранения
        addSaveButtonsToFieldsets();
    }

    // Запускаем когда DOM готов
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
