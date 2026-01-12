import os
import asyncio
import requests
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.filters import Command

BOT_TOKEN = os.getenv("BOT_TOKEN")
MONO_TOKEN = os.getenv("MONO_TOKEN")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# ---------- КНОПКА ОПЛАТИ ----------
pay_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="💳 Оплатити 600 грн", callback_data="pay_600")]
    ]
)

# ---------- /start ----------
@dp.message(Command("start"))
async def start(message: Message):
    await message.answer(
        "Привіт 👋\n\n"
        "Для продовження потрібно оплатити 600 грн 👇",
        reply_markup=pay_kb,
        parse_mode="Markdown"
    )

# ---------- СТВОРЕННЯ ОПЛАТИ ----------
@dp.callback_query(F.data == "pay_600")
async def create_invoice(call: CallbackQuery):

    headers = {
        "X-Token": MONO_TOKEN
    }

    data = {
        "amount": 60000,  # 600 грн
        "ccy": 980,
        "merchantPaymInfo": {
            "reference": str(call.from_user.id),
            "comment": "Оплата доступу"
        },
        "redirectUrl": "https://t.me/your_bot_username",
    }

    response = requests.post(
        "https://api.monobank.ua/api/merchant/invoice/create",
        json=data,
        headers=headers
    )

    if response.status_code != 200:
        await call.message.answer("❌ Помилка створення оплати. Спробуй пізніше.")
        return

    result = response.json()
    pay_url = result["pageUrl"]

    await call.message.answer(
        "👇 Натисни кнопку та оплати:\n\n"
        f"{pay_url}\n\n"
        "Після успішної оплати доступ відкриється автоматично ✅"
    )

# ---------- ЗАПУСК ----------
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())