import asyncio
import requests

from aiogram import Bot, Dispatcher, F
from aiogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery
)
from aiogram.filters import Command

# =====================
# НАЛАШТУВАННЯ
# =====================

BOT_TOKEN = "8333200799:AAFmOuLn2uidQrkjv6ODCMdija-_4lgL9sA"
MONO_TOKEN = "maxQzE_h0vmygXhmEqPAWIQ"

# =====================
# КНОПКА ОПЛАТИ
# =====================

pay_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="💳 Оплатити 600 грн", callback_data="pay_600")]
    ]
)

# =====================
# /start
# =====================

async def start(message: Message):
    await message.answer(
        "Привіт! 👋\n\nЩоб продовжити, натисни кнопку оплати 👇",
        reply_markup=pay_keyboard
    )

# =====================
# ОБРОБКА КНОПКИ ОПЛАТИ
# =====================

async def pay_clicked(callback: CallbackQuery):
    await callback.answer()  # прибирає "годинник" у кнопці

    headers = {
        "X-Token": MONO_TOKEN
    }

    data = {
        "amount": 60000,  # 600 грн у копійках
        "ccy": 980,
        "merchantPaymInfo": {
            "reference": "order_600",
            "destination": "Оплата послуги",
            "comment": "Оплата через Telegram-бот"
        },
        # тимчасово, просто щоб monobank не сварився
        "redirectUrl": "https://t.me/",
        "webHookUrl": "https://example.com/webhook"
    }

    response = requests.post(
        "https://api.monobank.ua/api/merchant/invoice/create",
        headers=headers,
        json=data,
        timeout=10
    )

    result = response.json()

    if "pageUrl" in result:
        await callback.message.answer(
            f"💳 Оплатіть за посиланням:\n\n{result['pageUrl']}"
        )
    else:
        await callback.message.answer(
            "❌ Не вдалося створити платіж.\nСпробуйте пізніше."
        )

# =====================
# ЗАПУСК БОТА
# =====================

async def main():
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    dp.message.register(start, Command("start"))
    dp.callback_query.register(pay_clicked, F.data == "pay_600")

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())