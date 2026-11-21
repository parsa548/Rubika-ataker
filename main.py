import asyncio
import logging

from database import init_db
from message_manager import MessageManager
from chat_manager import ChatManager
from task_manager import TaskManager


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)


async def main():

    logging.info("Rubika Manager is starting...")

    # راه‌اندازی دیتابیس
    await init_db()

    logging.info("Database initialized.")

    # ساخت مدیرها
    message_manager = MessageManager()
    chat_manager = ChatManager()
    task_manager = TaskManager()

    # بازیابی اطلاعات چت‌ها
    await chat_manager.load_chats()

    logging.info("Managers initialized.")

    print("سیستم مدیریت آماده است.")
    print("مدیریت پیام‌ها: فعال")
    print("مدیریت چت‌ها: فعال")
    print("مدیریت وظایف: فعال")

    try:
        await asyncio.Event().wait()

    finally:
        await chat_manager.stop_all()
        await task_manager.cancel_all()

        logging.info("System stopped safely.")


if __name__ == "__main__":
    try:
        asyncio.run(main())

    except KeyboardInterrupt:
        print("برنامه متوقف شد.")
