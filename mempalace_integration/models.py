#!/usr/bin/env python3
"""
Django приложение для интеграции MemPalace - системы памяти для ИИ.
Сохраняет историю чатов и позволяет восстанавливать контекст между сессиями.

Установка:
1. Добавить 'mempalace_integration' в INSTALLED_APPS
2. Запустить миграции: python manage.py migrate
3. Настроить MEMPALACE_PALACE_PATH в settings.py
"""

import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any

from django.conf import settings
from django.db import models
from django.utils import timezone

# Импортируем searcher из mempalace
try:
    from mempalace.searcher import search_memories, SearchError
    MEMPALACE_AVAILABLE = True
except ImportError:
    MEMPALACE_AVAILABLE = False
    search_memories = None
    SearchError = Exception

logger = logging.getLogger(__name__)


class ChatSession(models.Model):
    """Модель сессии чата."""
    
    session_id = models.CharField(max_length=255, unique=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    # Метаданные сессии
    user_agent = models.TextField(blank=True, null=True)
    topic = models.CharField(max_length=500, blank=True, default='')
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Сессия чата'
        verbose_name_plural = 'Сессии чатов'
    
    def __str__(self):
        return f"Session {self.session_id[:8]}... ({self.topic})"
    
    def save_to_mempalace(self, messages: List[Dict[str, Any]], wing: str = None) -> bool:
        """
        Сохранить историю сообщений в MemPalace.
        
        Args:
            messages: Список сообщений формата [{'role': 'user/assistant', 'content': '...'}]
            wing: Название крыла в MemPalace (по умолчанию session_id)
        
        Returns:
            True если успешно, False иначе
        """
        if not MEMPALACE_AVAILABLE:
            logger.error("MemPalace не установлен")
            return False
        
        wing = wing or f"session_{self.session_id[:8]}"
        palace_path = getattr(settings, 'MEMPALACE_PALACE_PATH', str(Path.home() / '.mempalace' / 'palace'))
        
        try:
            # Создаём временный файл с сообщениями
            temp_dir = Path(settings.MEDIA_ROOT) / 'mempalace_temp'
            temp_dir.mkdir(parents=True, exist_ok=True)
            
            temp_file = temp_dir / f"{self.session_id}.jsonl"
            with open(temp_file, 'w', encoding='utf-8') as f:
                for msg in messages:
                    f.write(json.dumps(msg, ensure_ascii=False) + '\n')
            
            # Импортируем через CLI mempalace
            import subprocess
            result = subprocess.run(
                ['mempalace', 'mine', str(temp_dir), '--mode', 'convos', '--wing', wing],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            # Очищаем временный файл
            temp_file.unlink(missing_ok=True)
            
            if result.returncode == 0:
                logger.info(f"Сессия {self.session_id} сохранена в MemPalace (wing: {wing})")
                return True
            else:
                logger.error(f"Ошибка сохранения в MemPalace: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error("Таймаут при сохранении в MemPalace")
            return False
        except Exception as e:
            logger.error(f"Ошибка при сохранении в MemPalace: {e}")
            return False
    
    def search_mempalace(self, query: str, n_results: int = 5) -> Dict[str, Any]:
        """
        Поиск в истории сессии через MemPalace.
        
        Args:
            query: Поисковый запрос
            n_results: Количество результатов
        
        Returns:
            Словарь с результатами поиска
        """
        if not MEMPALACE_AVAILABLE:
            return {"error": "MemPalace не установлен"}
        
        wing = f"session_{self.session_id[:8]}"
        palace_path = getattr(settings, 'MEMPALACE_PALACE_PATH', str(Path.home() / '.mempalace' / 'palace'))
        
        try:
            results = search_memories(
                query=query,
                palace_path=palace_path,
                wing=wing,
                n_results=n_results
            )
            return results
        except SearchError as e:
            return {"error": str(e)}
        except Exception as e:
            return {"error": f"Ошибка поиска: {e}"}


class ChatMessage(models.Model):
    """Модель сообщения чата."""
    
    ROLE_CHOICES = [
        ('user', 'Пользователь'),
        ('assistant', 'Ассистент'),
        ('system', 'Система'),
    ]
    
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='messages')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Метаданные для MemPalace
    is_saved = models.BooleanField(default=False)
    mempalace_wing = models.CharField(max_length=255, blank=True, null=True)
    
    class Meta:
        ordering = ['created_at']
        verbose_name = 'Сообщение'
        verbose_name_plural = 'Сообщения'
        indexes = [
            models.Index(fields=['session', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.role}: {self.content[:50]}..."
    
    def to_dict(self) -> Dict[str, Any]:
        """Конвертировать сообщение в словарь для MemPalace."""
        return {
            'role': self.role,
            'content': self.content,
            'timestamp': self.created_at.isoformat(),
            'session_id': self.session.session_id,
        }


class MemPalaceService:
    """Сервис для работы с MemPalace."""
    
    def __init__(self, palace_path: str = None):
        self.palace_path = palace_path or getattr(
            settings, 
            'MEMPALACE_PALACE_PATH', 
            str(Path.home() / '.mempalace' / 'palace')
        )
    
    def save_session(self, session: ChatSession) -> bool:
        """Сохранить всю сессию в MemPalace."""
        messages = session.messages.order_by('created_at').values_list('role', 'content', 'created_at')
        
        messages_list = [
            {
                'role': role,
                'content': content,
                'timestamp': timestamp.isoformat() if timestamp else None,
            }
            for role, content, timestamp in messages
        ]
        
        return session.save_to_mempalace(messages_list)
    
    def search_global(self, query: str, n_results: int = 10) -> Dict[str, Any]:
        """
        Глобальный поиск по всем сессиям в MemPalace.
        
        Args:
            query: Поисковый запрос
            n_results: Количество результатов
        
        Returns:
            Словарь с результатами поиска
        """
        if not MEMPALACE_AVAILABLE:
            return {"error": "MemPalace не установлен"}
        
        try:
            results = search_memories(
                query=query,
                palace_path=self.palace_path,
                n_results=n_results
            )
            return results
        except SearchError as e:
            return {"error": str(e)}
        except Exception as e:
            return {"error": f"Ошибка поиска: {e}"}
    
    def get_context_for_new_session(self, topics: List[str] = None) -> str:
        """
        Получить контекст для новой сессии на основе предыдущих разговоров.
        
        Args:
            topics: Список тем для поиска
        
        Returns:
            Строка с контекстом для system prompt
        """
        if not topics:
            topics = ["предыдущие разговоры", "контекст", "история"]
        
        all_results = []
        for topic in topics:
            results = self.search_global(topic, n_results=3)
            if 'results' in results:
                all_results.extend(results['results'])
        
        if not all_results:
            return ""
        
        # Формируем контекст
        context_parts = []
        context_parts.append("=== ПРЕДЫДУЩИЙ КОНТЕКСТ ИЗ MEMPALACE ===\n")
        
        for i, result in enumerate(all_results[:10], 1):
            wing = result.get('wing', 'unknown')
            text = result.get('text', '')
            similarity = result.get('similarity', 0)
            
            context_parts.append(f"[{i}] Wing: {wing}, Match: {similarity}")
            context_parts.append(f"    {text[:200]}...\n")
        
        context_parts.append("=== КОНЕЦ КОНТЕКСТА ===\n")
        
        return "\n".join(context_parts)


# Менеджер для автоматического сохранения сессий
class SessionManager:
    """Менеджер для управления сессиями и их сохранения в MemPalace."""
    
    @staticmethod
    def create_session(session_id: str, topic: str = '', **kwargs) -> ChatSession:
        """Создать новую сессию."""
        return ChatSession.objects.create(
            session_id=session_id,
            topic=topic,
            **kwargs
        )
    
    @staticmethod
    def end_session(session: ChatSession, auto_save: bool = True) -> bool:
        """
        Завершить сессию и optionally сохранить в MemPalace.
        
        Args:
            session: Сессия для завершения
            auto_save: Автоматически сохранить в MemPalace
        
        Returns:
            True если успешно сохранено
        """
        session.is_active = False
        session.save()
        
        if auto_save and session.messages.exists():
            service = MemPalaceService()
            return service.save_session(session)
        
        return True
    
    @staticmethod
    def restore_context(session_id: str) -> str:
        """
        Восстановить контекст для сессии из MemPalace.
        
        Args:
            session_id: ID сессии
        
        Returns:
            Строка с контекстом
        """
        service = MemPalaceService()
        return service.get_context_for_new_session([f"session {session_id[:8]}"])
