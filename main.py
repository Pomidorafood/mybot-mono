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

# --- КНОПКА ОПЛАТИ ---
pay_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="💳 Оплатити 600 грн", callback_data="pay_600")]
    ]
)

paid_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="✅ Я оплатив(ла)", callback_data="check_pay")]
    ]
)

# Тимчасове зберігання інвойсів
user_invoices = {}

# --- /start ---
@dp.message(Command("start"))
async def start(message: Message):
    await message.answer(
        "Привіт 👋\n\nДля продовження потрібно оплатити 600 грн.",
        reply_markup=pay_kb,
        parse_mode="Markdown"
    )

# --- СТВОРЕННЯ ІНВОЙСУ ---
@dp.callback_query(F.data == "pay_600")
async def create_invoice(call: CallbackQuery):
    headers = {
        "X-Token": MONO_TOKEN
    }

    data = {
        "amount": 60000,  # 600 грн у копійках
        "ccy": 980,
        "merchantPaymInfo": {
            "reference": str(call.from_user.id),
            "comment": "Оплата доступу",
        },
        "redirectUrl": "https://t.me",
        "webHookUrl": ""
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

    user_invoices[call.from_user.id] = invoice_id

    await call.message.answer(
        f"👇 Оплати за посиланням:\n{pay_url}",
        reply_markup=paid_kb
    )

# --- ПЕРЕВІРКА ОПЛАТИ ---
@dp.callback_query(F.data == "check_pay")
async def check_payment(call: CallbackQuery):
    invoice_id = user_invoices.get(call.from_user.id)

    if not invoice_id:
        await call.message.answer("❌ Оплату не знайдено. Натисни «Оплатити» ще раз.")
        return

    headers = {
        "X-Token": MONO_TOKEN
    }

    r = requests.get(
        f"https://api.monobank.ua/api/merchant/invoice/status?invoiceId={invoice_id}",
        headers=headers
    )

    if r.status_code != 200:
        await call.message.answer("⏳ Не вдалося перевірити оплату, спробуй ще раз.")
        return

    status = r.json().get("status")

    if status == "paid":
        await call.message.answer(
            "🎉 **Оплата успішна!**\n\nОсь твій доступ 👇\nhttps://t.me/your_private_channel",
            parse_mode="Markdown"
        )
        user_invoices.pop(call.from_user.id, None)
    else:
        await call.message.answer(
            "❌ Оплату не знайдено.\n\n"
            "Переконайся, що:\n"
            "• оплачено **600 грн**\n"
            "• платіж завершений\n\n"
            "Спробуй ще раз через кілька секунд ⏳"
        )

# --- ЗАПУСК ---
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())