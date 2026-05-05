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
            state[id] = fieldset.classList.contains('collapsed');
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
                    if (state[id]) {
                        fieldset.classList.add('collapsed');
                    } else {
                        fieldset.classList.remove('collapsed');
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
            
            // Находим legend (заголовок fieldset)
            const legend = fieldset.querySelector('legend');
            if (!legend) return;
            
            // Создаём контейнер для кнопки справа от заголовка
            const btnContainer = document.createElement('div');
            btnContainer.className = 'section-save-btn-container';
            btnContainer.style.cssText = 'float: right; margin-left: auto;';
            
            // Создаём кнопку
            const saveBtn = document.createElement('button');
            saveBtn.type = 'button';
            saveBtn.className = 'section-save-btn default';
            saveBtn.textContent = '💾 Сохранить';
            saveBtn.style.cssText = 'padding: 4px 10px; font-size: 0.85rem; height: auto; line-height: normal;';
            
            // Обработчик клика
            saveBtn.addEventListener('click', function(e) {
                e.preventDefault();
                
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
            
            btnContainer.appendChild(saveBtn);
            legend.appendChild(btnContainer);
            
            // Также отслеживаем клик по заголовку для обновления состояния
            legend.addEventListener('click', function(e) {
                // Небольшая задержка чтобы класс collapsed успел примениться
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
        
        // Также слушаем изменения состояния через делегирование событий
        document.addEventListener('DOMContentLoaded', function() {
            // Повторно восстанавливаем состояние на случай динамической подгрузки
            restoreFieldsetsState();
        });
    }

    // Запускаем когда DOM готов
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
