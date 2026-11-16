import asyncio
import logging


class TaskManager:

    def __init__(self):
        self.tasks = {}
        self.lock = asyncio.Lock()

    async def create_task(self, chat_id, coroutine):
        chat_id = str(chat_id)

        async with self.lock:

            existing = self.tasks.get(chat_id)

            if existing and not existing.done():
                coroutine.close()
                return False

            task = asyncio.create_task(coroutine)

            self.tasks[chat_id] = task

            task.add_done_callback(
                lambda t: self._task_finished(chat_id, t)
            )

            logging.info(
                "Task created for chat %s", chat_id
            )

            return True

    def _task_finished(self, chat_id, task):
        if self.tasks.get(chat_id) is task:
            self.tasks.pop(chat_id, None)

        if task.cancelled():
            return

        error = task.exception()

        if error:
            logging.error(
                "Task error in chat %s: %s",
                chat_id,
                error
            )

    async def cancel_task(self, chat_id):
        chat_id = str(chat_id)

        async with self.lock:
            task = self.tasks.get(chat_id)

            if not task:
                return False

            task.cancel()

        try:
            await task
        except asyncio.CancelledError:
            pass

        return True

    async def cancel_all(self):
        async with self.lock:
            tasks = list(self.tasks.values())

            for task in tasks:
                task.cancel()

        if tasks:
            await asyncio.gather(
                *tasks,
                return_exceptions=True
            )

        self.tasks.clear()

        logging.info("All tasks cancelled")

    def is_running(self, chat_id):
        task = self.tasks.get(str(chat_id))

        return bool(task and not task.done())

    def running_count(self):
        return sum(
            1 for task in self.tasks.values()
            if not task.done()
        )
