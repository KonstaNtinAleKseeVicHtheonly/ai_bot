'''Файл для сохранения сообщений от юзера при текстовом диалоге с AI что бы AI запоминал историю диалога а не отвечал каждый раз заново'''
from collections import defaultdict
from typing import Dict, List, Optional
import threading
import time

import asyncio
from contextlib import asynccontextmanager


class ChatHistory:
    def __init__(self, max_history_length: int = 20, cleanup_hours: int = 24):
        """
        Синхронный менеджер истории чатов с очисткой старых данных
        
        Args:
            max_history_length: максимальное количество сообщений на чат
            cleanup_hours: через сколько часов очищать неактивные чаты
        """
        self.histories: Dict[int, List[Dict]] = defaultdict(list)
        self.last_access: Dict[int, float] = {}  # Время последнего доступа
        self.max_history_length = max_history_length
        self.cleanup_hours = cleanup_hours
        self.lock = threading.RLock()  # Reentrant lock для thread safety
        self.system_prompt = "Отвечай лаконично и емко"
        # Запускаем фоновую очистку
        self._start_cleanup_thread()
    
    def _update_access_time(self, chat_id: int):
        """Обновить время последнего доступа"""
        self.last_access[chat_id] = time.time()
    
    def get_messages(self, chat_id: int) -> List[Dict]:
        """Получить историю сообщений для чата"""
        with self.lock:
            self._update_access_time(chat_id)
            # Возвращаем копию, чтобы избежать изменений извне
            return self.histories.get(chat_id, []).copy()
    
    def add_message(self, chat_id: int,content: str) -> None:
        """Добавить сообщение в историю"""
        if not content:
            return
        
        with self.lock:
            self._update_access_time(chat_id)
            
            # Если история пуста, добавляем system prompt
            if chat_id not in self.histories or not self.histories[chat_id]:
                self.histories[chat_id] = [
                    {"role": "system", "content": self.system_prompt}
                ]
            
            # Добавляем новое сообщение
            self.histories[chat_id].append({"role": 'user', "content": content})
            
            # Обрезаем историю если нужно
            self._truncate_history(chat_id)
    
    def _truncate_history(self, chat_id: int) -> None:
        """Обрезать историю до максимальной длины"""
        if chat_id not in self.histories:
            return
        
        messages = self.histories[chat_id]
        if len(messages) > self.max_history_length:
            # Оставляем system и последние сообщения
            self.histories[chat_id] = [messages[0]] + messages[-(self.max_history_length - 1):]
    
    def clear_history(self, chat_id: int, keep_system: bool = True) -> None:
        """Очистить историю диалога"""
        with self.lock:
            if chat_id in self.histories:
                if keep_system and self.histories[chat_id]:
                    # Оставляем только system prompt
                    self.histories[chat_id] = [self.histories[chat_id][0]]
                else:
                    # Полная очистка
                    del self.histories[chat_id]
                    if chat_id in self.last_access:
                        del self.last_access[chat_id]
    
    def _cleanup_old_chats(self):
        """Очистить истории, к которым не обращались N часов"""
        with self.lock:
            now = time.time()
            cutoff = now - (self.cleanup_hours * 3600)
            
            to_remove = [
                chat_id for chat_id, last_time in self.last_access.items()
                if last_time < cutoff
            ]
            
            for chat_id in to_remove:
                del self.histories[chat_id]
                del self.last_access[chat_id]
            
            if to_remove:
                print(f"Очищено {len(to_remove)} неактивных чатов")
    
    def _start_cleanup_thread(self):
        """Запустить фоновый поток для очистки"""
        def cleanup_worker():
            while True:
                time.sleep(3600)  # Каждый час
                self._cleanup_old_chats()
        
        thread = threading.Thread(target=cleanup_worker, daemon=True)
        thread.start()
    
    def __del__(self):
        """Деструктор для остановки cleanup потока"""
        # В Python потоки-демоны остановятся автоматически
        pass
    

class ChatHistory_2:
    """
    Синхронный менеджер истории чатов для использования в асинхронном боте.
    Все операции выполняются мгновенно (nanosec) в памяти, блокировки не нужны.
    Для асинхронного доступа используем asyncio.Lock на уровне chat_id.
    """
    
    def __init__(self, max_history_length: int = 20):
        """
        Args:
            max_history_length: максимальное количество сообщений на чат (включая system)
        """
        self.histories: Dict[int, List[Dict]] = defaultdict(list)
        self.max_history_length = max_history_length
        self.system_prompt = "Отвечай лаконично и емко"
        
        # Async locks для конкурентного доступа
        self._chat_locks: Dict[int, asyncio.Lock] = defaultdict(asyncio.Lock)
        self._global_lock = asyncio.Lock()
    
    @asynccontextmanager
    async def _chat_context(self, chat_id: int):
        """Контекстный менеджер для безопасного доступа к конкретному чату"""
        async with self._global_lock:
            if chat_id not in self._chat_locks:
                self._chat_locks[chat_id] = asyncio.Lock()
            lock = self._chat_locks[chat_id]
        async with lock:
            yield
    
    async def add_message(self, chat_id: int,role:str, content: str) -> None:
        """Добавить сообщение в историю"""
        if not content:
            return
        
        async with self._chat_context(chat_id):
            # Инициализируем историю если пуста
            if not self.histories[chat_id]:
                self.histories[chat_id] = [
                    {"role": "system", "content": self.system_prompt}
                ]
            
            # Добавляем сообщение
            self.histories[chat_id].append({"role": role, "content": content})
            
            # Обрезаем если превышен лимит
            if len(self.histories[chat_id]) > self.max_history_length:
                self.histories[chat_id] = [
                    self.histories[chat_id][0]  # system prompt
                ] + self.histories[chat_id][-(self.max_history_length - 1):]
    
    async def get_messages(self, chat_id: int) -> List[Dict]:
        """Получить историю сообщений (возвращает копию)"""
        async with self._chat_context(chat_id):
            if not self.histories[chat_id]:
                return [{"role": "system", "content": self.system_prompt}]
            return self.histories[chat_id].copy()
    
    async def clear_history(self, chat_id: int) -> None:
        """Полностью очистить историю чата"""
        async with self._chat_context(chat_id):
            self.histories[chat_id] = [
                {"role": "system", "content": self.system_prompt}
            ]
    
    async def get_stats(self) -> Dict:
        """Получить статистику по всем чатам"""
        # Не блокируем все чаты для статистики
        async with self._global_lock:
            total_chats = len(self.histories)
            total_messages = sum(len(msgs) for msgs in self.histories.values())
            
            return {
                "total_chats": total_chats,
                "total_messages": total_messages,
                "avg_messages": round(total_messages / total_chats, 2) if total_chats else 0,
            }
    
    async def cleanup_inactive(self, max_inactive_hours: int = 24) -> int:
        """
        Очистить истории неактивных чатов
        Возвращает количество очищенных чатов
        """
        # Внимание: этот метод упрощен, так как в памяти нет timestamp сообщений
        # В production нужно хранить время последнего сообщения
        
        cleared = 0
        async with self._global_lock:
            # Удаляем старые локсы (примерно)
            old_chats = list(self._chat_locks.keys())[:100]  # Ограничиваем выборку
            
            for chat_id in old_chats:
                # Если история содержит только system prompt и нет активности
                if chat_id in self.histories and len(self.histories[chat_id]) == 1:
                    async with self._chat_context(chat_id):
                        if chat_id in self.histories and len(self.histories[chat_id]) == 1:
                            del self.histories[chat_id]
                            cleared += 1
        
        return cleared
