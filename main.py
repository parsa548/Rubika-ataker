import asyncio
import logging

from database import init_db
from message_manager import MessageManager
from chat_manager import ChatManager
from task_manager import TaskManager

logging.basicConfig(level=logging.INFO)


async def main():
    await init_db()

    messages = MessageManager()
    chats = ChatManager()
    tasks = TaskManager()

    await chats.load_chats()

    print("\nRubika Manager")
    print("برای مشاهده دستورات بنویس: /help")

    try:
        while True:
            command = (await asyncio.to_thread(
                input, "\nManager > "
            )).strip()

            parts = command.split(maxsplit=2)
            if not parts:
                continue

            cmd = parts[0].lower()

            if cmd == "/help":
                print("""
/add متن
/list
/count
/remove شناسه
/start شناسه_چت
/stop شناسه_چت
/stopall
/time شناسه_چت ثانیه
/status شناسه_چت
/exit
""")

            elif cmd == "/add" and len(parts) > 1:
                print("Add:", await messages.add(command[5:]))

            elif cmd == "/list":
                for item in await messages.list_messages():
                    print(item)

            elif cmd == "/count":
                print("Count:", await messages.count())

            elif cmd == "/remove" and len(parts) > 1:
                await messages.remove(int(parts[1]))
                print("Message removed.")

            elif cmd == "/start" and len(parts) > 1:
                print("Start:", await chats.start(parts[1]))

            elif cmd == "/stop" and len(parts) > 1:
                print("Stop:", await chats.stop(parts[1]))

            elif cmd == "/stopall":
                print("Stopped:", await chats.stop_all())

            elif cmd == "/time" and len(parts) > 2:
                print(
                    "Time:",
                    await chats.set_interval(
                        parts[1], int(parts[2])
                    )
                )

            elif cmd == "/status" and len(parts) > 1:
                print(await chats.status(parts[1]))

            elif cmd == "/exit":
                break

            else:
                print("دستور نامعتبر است. /help را بزن.")

    finally:
        await chats.stop_all()
        await tasks.cancel_all()
        print("Manager closed.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nبرنامه متوقف شد.")
        
