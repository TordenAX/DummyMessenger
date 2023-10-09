import asyncio
from aiohttp import web
import sqlite3
from datetime import datetime


# Функция для инициализации базы данных (создание таблицы, если она не существует)
def init_database():
    conn = sqlite3.connect('messages.db')
    c = conn.cursor()

    c.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY,
            sender TEXT,
            text TEXT,
            date TIMESTAMP,
            sender_counter INTEGER,
            total_counter INTEGER
        )
    ''')

    conn.commit()
    conn.close()


# Функция для сохранения сообщения в базу данных
def save_message(sender, text, sender_counter, total_counter):
    conn = sqlite3.connect('messages.db')
    c = conn.cursor()

    current_date = datetime.now().isoformat()

    c.execute('''
        INSERT INTO messages (sender, text, date, sender_counter, total_counter)
        VALUES (?, ?, ?, ?, ?)
    ''', (sender, text, current_date, sender_counter, total_counter))

    conn.commit()
    conn.close()


# Функция для получения последних сообщений из базы данных
def get_last_messages():
    conn = sqlite3.connect('messages.db')
    c = conn.cursor()

    c.execute('''
        SELECT sender, text, date, sender_counter, total_counter FROM messages
        ORDER BY id DESC
        LIMIT 10
    ''')

    messages = []
    for row in reversed(c.fetchall()):
        sender, text, date, sender_counter, total_counter = row
        messages.append({
            'sender': sender,
            'text': text,
            'date': date,
            'sender_counter': sender_counter,
            'total_counter': total_counter
        })

    conn.close()
    return messages


async def receive_message(request):
    data = await request.json()
    sender = data.get('sender')
    text = data.get('text')

    # Получение последнего счётчика сообщений отправителя
    conn = sqlite3.connect('messages.db')
    c = conn.cursor()

    c.execute('''
        SELECT MAX(sender_counter) FROM messages WHERE sender = ?
    ''', (sender,))

    result = c.fetchone()
    if result and result[0]:
        sender_counter = result[0] + 1
        total_counter = result[0] + 1
    else:
        sender_counter = 1
        total_counter = 1

    # Сохранение сообщения в базу данных
    save_message(sender, text, sender_counter, total_counter)

    # Получение последних сообщений
    messages = get_last_messages()

    return web.json_response(messages)


async def main():
    app = web.Application()
    app.router.add_post('/', receive_message)

    # Инициализация базы данных
    init_database()

    runner = web.AppRunner(app)
    await runner.setup()

    site = web.TCPSite(runner, 'localhost', 8000)
    await site.start()

    # Ожидание завершения работы сервера
    await asyncio.Event().wait()


loop = asyncio.get_event_loop()
loop.run_until_complete(main())
