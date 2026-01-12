import os
import asyncio
import logging
import requests
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiohttp import web

# ================= НАСТРОЙКИ =================

BOT_TOKEN = os.getenv("BOT_TOKEN")
MONO_TOKEN = os.getenv("MONO_TOKEN")

WEBHOOK_PATH = "/monobank-webhook"
WEBHOOK_PORT = int(os.getenv("PORT", 10000))

PRIVATE_LINK = "https://t.me/+vXrhaI-dAWJiNWJi"  # 🔴 ЗАМІНИ НА СВІЙ 

# ============================================

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Зберігаємо invoiceId -> user_id
invoices = {}

# ================= КНОПКА ОПЛАТИ =================

pay_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="💳 Оплатити 600 грн", callback_data="pay")]
    ]
)

# ================= /start =================

@dp.message(Command("start"))
async def start(message: Message):
    await message.answer(
        "Привіт 👋\n\nДля продовження потрібно оплатити 600 грн 👇",
        reply_markup=pay_kb,
        parse_mode="Markdown"
    )

# ================= СТВОРЕННЯ ІНВОЙСУ =================

@dp.callback_query(F.data == "pay")
async def create_invoice(call):
    headers = {
        "X-Token": MONO_TOKEN
    }

    data = {
        "amount": 60000,
        "ccy": 980,
        "merchantPaymInfo": {
            "reference": str(call.from_user.id),
            "comment": "Оплата доступу",
        },
        "redirectUrl": f"https://t.me/{(await bot.get_me()).username}",
        "webHookUrl": os.getenv("RENDER_EXTERNAL_URL") + WEBHOOK_PATH
    }

    r = requests.post(
        "https://api.monobank.ua/api/merchant/invoice/create",
        json=data,
        headers=headers
    )

    if r.status_code != 200:
        await call.message.answer("❌ Помилка створення оплати. Спробуй пізніше.")
        return

    res = r.json()
    invoice_id = res["invoiceId"]
    pay_url = res["pageUrl"]

    invoices[invoice_id] = call.from_user.id

    await call.message.answer(
        f"👇 Натисни та оплати:\n{pay_url}\n\n"
        "Після оплати доступ відкриється автоматично ✅"
    )

# ================= WEBHOOK MONOBANK =================

async def monobank_webhook(request):
    data = await request.json()

    invoice_id = data.get("invoiceId")
    status = data.get("status")

    if status == "paid" and invoice_id in invoices:
        user_id = invoices.pop(invoice_id)

        await bot.send_message(
            user_id,
            f"🎉 **Оплата успішна!**\n\n"
            f"Ось твій доступ 👇\n{PRIVATE_LINK}",
            parse_mode="Markdown"
        )

    return web.Response(text="ok")

# ================= ЗАПУСК =================

async def main():
    app = web.Application()
    app.router.add_post(WEBHOOK_PATH, monobank_webhook)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", WEBHOOK_PORT)
    await site.start()

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())