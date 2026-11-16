import asyncio
import random

from database import (
    add_message,
    get_messages,
    delete_message,
    count_messages
)


class MessageManager:

    def __init__(self):
        self._cycle = []
        self._lock = asyncio.Lock()

    async def add(self, text):
        text = text.strip()

        if not text:
            return False

        await add_message(text)
        self._cycle.clear()
        return True

    async def remove(self, message_id):
        await delete_message(message_id)
        self._cycle.clear()

    async def list_messages(self):
        return await get_messages()

    async def count(self):
        return await count_messages()

    async def next_message(self):
        async with self._lock:

            if not self._cycle:
                messages = await get_messages()

                if not messages:
                    return None

                self._cycle = list(messages)
                random.shuffle(self._cycle)

            message_id, text = self._cycle.pop()

            return {
                "id": message_id,
                "text": text
            }
