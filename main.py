import asyncio
import os
import time
import requests

from aiogram import Bot, Dispatcher, F
from aiogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery,
)
from aiogram.filters import Command

# ======================
# ENV VARIABLES
# ======================
BOT_TOKEN = os.getenv("BOT_TOKEN")
MONO_TOKEN = os.getenv("MONO_TOKEN")

PAY_AMOUNT = 600  # грн
PAY_LINK = "https://pay.monobank.ua/2601129zmXMpj3Y4tZS1"

# ======================
# BOT INIT
# ======================
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# ======================
# KEYBOARD
# ======================
pay_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="💳 Оплатити 600 грн", url=PAY_LINK)],
        [InlineKeyboardButton(text="✅ Я оплатив(ла)", callback_data="check_payment")]
    ]
)

# ======================
# MONOBANK CHECK
# ======================
def check_monobank_payment(amount: int) -> bool:
    """
    Перевіряє, чи був платіж на суму amount (грн)
    """
    url = "https://api.monobank.ua/personal/statement/0"
    headers = {"X-Token": MONO_TOKEN}

    now = int(time.time())
    from_time = now - 3600  # остання година

    params = {
        "from": from_time,
        "to": now,
    }

    response = requests.get(url, headers=headers, params=params)

    if response.status_code != 200:
        return False

    operations = response.json()

    for op in operations:
        if op.get("amount") == amount * 100:  # mono в копійках
            return True

    return False

# ======================
# HANDLERS
# ======================
@dp.message(Command("start"))
async def start(message: Message):
    await message.answer(
        "Привіт 👋\n\n"
        "Для продовження потрібно оплатити 600 грн.\n"
        "Після оплати натисни кнопку нижче 👇",
        reply_markup=pay_keyboard,
        parse_mode="Markdown"
    )

@dp.callback_query(F.data == "check_payment")
async def check_payment(callback: CallbackQuery):
    await callback.answer("Перевіряю оплату ⏳")

    if check_monobank_payment(PAY_AMOUNT):
        await callback.message.answer(
            "✅ **Оплату підтверджено!**\n\n"
            "Дякую ❤️ Доступ відкрито.",
            parse_mode="Markdown"
        )
    else:
        await callback.message.answer(
            "❌ Оплату не знайдено.\n\n"
            "Переконайся, що:\n"
            "• оплата була саме **600 грн**\n"
            "• ти вже оплатив(ла)\n\n"
            "Спробуй ще раз через кілька секунд."
        )

# ======================
# START
# ======================
async def main():
    await dp.start_polling(bot)

if __name__  == "__main__":
    asyncio.run(main())