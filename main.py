import asyncio
import os

from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command

# 🔐 Токени беремо з Environment Variables
BOT_TOKEN = os.getenv("BOT_TOKEN")
MONO_TOKEN = os.getenv("MONO_TOKEN")

pay_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="💳 Оплатити 600 грн", callback_data="pay")]
    ]
)

async def start(message: Message):
    await message.answer(
        "Привіт 👋\n\nЩоб отримати доступ, потрібно оплатити 600 грн.",
        reply_markup=pay_keyboard
    )

async def pay_clicked(callback):
    await callback.message.answer(
        "⏳ Перевіряю оплату...\n\n(поки що це тест, далі підключимо Monobank)"
    )
    await callback.answer()

async def main():
    if not BOT_TOKEN:
        raise ValueError("❌ BOT_TOKEN не знайдено")

    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    dp.message.register(start, Command("start"))
    dp.callback_query.register(pay_clicked, F.data == "pay")

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())