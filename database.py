import os
import aiosqlite

DB_PATH = os.getenv("DB_PATH", "messages.db")


async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:

        await db.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                text TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        await db.execute("""
            CREATE TABLE IF NOT EXISTS chats (
                chat_id TEXT PRIMARY KEY,
                is_active INTEGER DEFAULT 0,
                interval INTEGER DEFAULT 15,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        await db.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        """)

        await db.commit()


async def get_connection():
    return await aiosqlite.connect(DB_PATH)


async def add_message(text):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO messages (text) VALUES (?)",
            (text,)
        )
        await db.commit()


async def get_messages():
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT id, text FROM messages ORDER BY id"
        )
        return await cursor.fetchall()


async def delete_message(message_id):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "DELETE FROM messages WHERE id = ?",
            (message_id,)
        )
        await db.commit()


async def count_messages():
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT COUNT(*) FROM messages"
        )
        result = await cursor.fetchone()
        return result[0]


async def save_chat(chat_id, interval=15):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT INTO chats (chat_id, interval)
            VALUES (?, ?)
            ON CONFLICT(chat_id)
            DO UPDATE SET interval = excluded.interval
        """, (str(chat_id), interval))
        await db.commit()


async def set_chat_status(chat_id, status):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE chats SET is_active = ? WHERE chat_id = ?",
            (int(status), str(chat_id))
        )
        await db.commit()


async def get_chats():
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT chat_id, is_active, interval FROM chats"
        )
        return await cursor.fetchall()
