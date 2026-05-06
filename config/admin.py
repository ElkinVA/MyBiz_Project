# config/admin.py
"""
Кастомизация админ-панели Django.
Скрывает ненужные разделы и настраивает отображение.
"""
from django.contrib import admin
from django.contrib.admin.sites import AdminSite
from auditlog.models import LogEntry


class MyBizAdminSite(AdminSite):
    """Кастомный сайт администрирования"""
    site_header = "MyBiz Администрирование"
    site_title = "MyBiz Админ"
    index_title = "Управление контентом"

    def has_permission(self, request):
        """Разрешаем доступ только авторизованным пользователям"""
        return request.user.is_active and request.user.is_staff

    def get_app_list(self, request, app_label=None):
        """
        Кастомизируем список приложений, скрывая ненужные разделы.
        """
        app_dict = self._build_app_dict(request, app_label)
        
        # Фильтруем приложения и модели
        filtered_apps = []
        for app in app_dict.values():
            app_name = app['name']
            
            # Пропускаем приложение Audit log полностью
            if app_name == 'Auditlog':
                continue
            
            # Фильтруем модели внутри приложения Auth
            if app_name == 'Authentication and Authorization':
                # Оставляем только группы и пользователей, но скрываем их
                # Полностью убираем раздел Users and groups
                continue
            
            # Для остальных приложений фильтруем модели
            filtered_models = []
            for model in app['models']:
                model_name = model['name']
                
                # Скрываем Запросы о поступлении (StockNotification)
                if model_name == 'Stock notification':
                    continue
                
                # Скрываем Подписчиков (NewsletterSubscriber)
                if model_name == 'Newsletter subscriber':
                    continue
                
                # Скрываем записи журнала аудита
                if model_name == 'Log entry':
                    continue
                
                filtered_models.append(model)
            
            # Добавляем приложение только если есть модели
            if filtered_models:
                app['models'] = filtered_models
                filtered_apps.append(app)
        
        return filtered_apps


# Переопределяем стандартный сайт админирования
admin.site = MyBizAdminSite(name='admin')
