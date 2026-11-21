import asyncio
import logging

from database import (
    save_chat,
    set_chat_status,
    get_chats
)


class ChatManager:

    def __init__(self):
        self.tasks = {}
        self.intervals = {}
        self.active_chats = set()
        self.lock = asyncio.Lock()

    async def load_chats(self):
        async with self.lock:
            chats = await get_chats()

            self.active_chats.clear()
            self.intervals.clear()

            for chat_id, active, interval in chats:
                chat_id = str(chat_id)

                self.intervals[chat_id] = interval

                # بعد از راه‌اندازی مجدد،
                # چت‌ها تا شروع مجدد، غیرفعال هستند.
                if active:
                    await set_chat_status(chat_id, False)

            logging.info("Chats loaded successfully")

    async def start(self, chat_id):
        chat_id = str(chat_id)

        async with self.lock:
            if chat_id in self.active_chats:
                return False

            interval = self.intervals.get(chat_id, 15)

            await save_chat(chat_id, interval)
            await set_chat_status(chat_id, True)

            self.active_chats.add(chat_id)

            logging.info("Chat %s activated", chat_id)

            return True

    async def stop(self, chat_id):
        chat_id = str(chat_id)

        async with self.lock:
            if chat_id not in self.active_chats:
                return False

            await set_chat_status(chat_id, False)

            self.active_chats.discard(chat_id)

            logging.info("Chat %s stopped", chat_id)

            return True

    async def set_interval(self, chat_id, seconds):
        chat_id = str(chat_id)

        if isinstance(seconds, bool) or not isinstance(seconds, int):
            raise ValueError("Interval must be an integer")

        if seconds < 15:
            raise ValueError(
                "Minimum interval is 15 seconds"
            )

        async with self.lock:
            await save_chat(chat_id, seconds)

            self.intervals[chat_id] = seconds

            logging.info(
                "Interval for chat %s set to %s seconds",
                chat_id,
                seconds
            )

            return True

    async def status(self, chat_id):
        chat_id = str(chat_id)

        async with self.lock:
            return {
                "chat_id": chat_id,
                "active": chat_id in self.active_chats,
                "interval": self.intervals.get(
                    chat_id, 15
                )
            }

    async def stop_all(self):
        async with self.lock:
            chats = list(self.active_chats)

            for chat_id in chats:
                await set_chat_status(chat_id, False)

            self.active_chats.clear()

            logging.info("All chats stopped")

            return len(chats)
