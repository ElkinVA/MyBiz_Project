"""
Сигналы для автоматического сохранения сессий в MemPalace.
"""

from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.conf import settings

from .models import ChatSession, ChatMessage, SessionManager


@receiver(pre_save, sender=ChatSession)
def on_session_update(sender, instance, **kwargs):
    """
    При обновлении сессии (например, установке is_active=False)
    автоматически сохраняем её в MemPalace.
    """
    if instance.pk:  # Только для существующих объектов
        try:
            old_instance = ChatSession.objects.get(pk=instance.pk)
            # Если сессия была активна и теперь становится неактивной
            if old_instance.is_active and not instance.is_active:
                # Сохранение будет выполнено в post_save
                instance._pending_mempalace_save = True
        except ChatSession.DoesNotExist:
            pass


@receiver(post_save, sender=ChatSession)
def on_session_saved(sender, instance, created, **kwargs):
    """
    После сохранения сессии проверяем, нужно ли сохранить в MemPalace.
    """
    if not created and getattr(instance, '_pending_mempalace_save', False):
        # Автоматическое сохранение при завершении сессии
        if getattr(settings, 'MEMPALACE_AUTO_SAVE', True):
            SessionManager.end_session(instance, auto_save=True)
        instance._pending_mempalace_save = False
