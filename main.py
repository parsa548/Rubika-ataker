import asyncio
import logging

from database import init_db


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)


async def main():
    logging.info("Rubika Manager is starting...")

    await init_db()

    logging.info("Database initialized successfully.")
    print("سیستم مدیریت آماده است.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("برنامه متوقف شد.")
