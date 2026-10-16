"""
Userbot с reply-кнопками.
Команда: /send @жертва (ответом на сообщение бота)
"""

import os
import asyncio
from telethon import TelegramClient, events
from telethon.tl.types import ReplyKeyboardMarkup, KeyboardButtonRow, KeyboardButton, ReplyKeyboardRemove

API_ID = int(os.environ.get("API_ID", "39450533"))
API_HASH = os.environ.get("API_HASH", "52a50527f3fd4d9c1cba720590e618fe")
SESSION = "session"

print("Импорт завершён", flush=True)
client = TelegramClient(SESSION, API_ID, API_HASH)

# user_id -> original message text
pending = {}


@client.on(events.NewMessage(outgoing=True, pattern=r'(?i)^/send'))
async def on_send(event):
    print(f"Получил /send: {event.raw_text}", flush=True)
    if not event.is_reply:
        await event.reply("Ответь на сообщение с оффером")
        return
    reply = await event.get_reply_message()
    text = reply.raw_text or reply.text or ""
    if not text:
        await event.reply("Нет текста")
        return
    parts = event.raw_text.split(maxsplit=1)
    if len(parts) < 2:
        await event.reply("Формат: /send @username")
        return
    target = parts[1].strip()
    try:
        entity = await client.get_entity(target)
        markup = ReplyKeyboardMarkup(
            rows=[KeyboardButtonRow(buttons=[
                KeyboardButton(text="✗ Отклонить"),
                KeyboardButton(text="✓ Принять")
            ])],
            resize=True,
            one_time_keyboard=True
        )
        sent = await client.send_message(entity, text, buttons=markup)
        pending[entity.id] = text
        print(f"Отправлено в {entity.id}", flush=True)
        await event.delete()
    except Exception as e:
        print(f"Ошибка: {e}", flush=True)
        await event.reply(f"Ошибка: {e}")


@client.on(events.NewMessage(incoming=True))
async def on_user_action(event):
    uid = event.sender_id
    if uid not in pending:
        return
    txt = event.raw_text or ""
    if txt not in ("✗ Отклонить", "✓ Принять"):
        return
    if txt == "✗ Отклонить":
        await event.reply("Предложение отклонено.", buttons=ReplyKeyboardRemove())
    else:
        await event.reply(
            "Предложение о продаже успешно принято.\n\nПередайте подарок покупателю.",
            buttons=ReplyKeyboardRemove()
        )
    del pending[uid]


async def main():
    print("СТАРТ", flush=True)
    await client.start()
    print("Userbot запущен.", flush=True)
    await client.run_until_disconnected()


if __name__ == "__main__":
    print("Запуск main", flush=True)
    asyncio.run(main())
