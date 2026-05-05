/**
 * messages-auto-hide.js
 * Автоматическое скрытие всплывающих сообщений в админ-панели Django через 5 секунд
 */

(function() {
    'use strict';

    /**
     * Скрывает сообщения с плавной анимацией
     */
    function hideMessages() {
        // Находим все сообщения в админке
        const messages = document.querySelectorAll('#content .messagelist li, .messagelist li');
        
        if (messages.length === 0) return;
        
        // Через 5 секунд скрываем сообщения
        setTimeout(function() {
            messages.forEach(function(msg) {
                // Добавляем плавное исчезновение
                msg.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
                msg.style.opacity = '0';
                msg.style.transform = 'translateY(-10px)';
                
                // Удаляем элемент из DOM после завершения анимации
                setTimeout(function() {
                    if (msg.parentNode) {
                        msg.remove();
                    }
                    
                    // Если список сообщений пустой, удаляем и его
                    const messageList = document.querySelector('.messagelist');
                    if (messageList && messageList.children.length === 0) {
                        messageList.remove();
                    }
                }, 500);
            });
        }, 5000);
    }

    // Запускаем когда DOM готов
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', hideMessages);
    } else {
        hideMessages();
    }
})();
