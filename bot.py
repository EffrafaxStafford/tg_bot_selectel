import asyncio
import httpx

from aiogram import Bot, Dispatcher
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup

from selectel import get_forecast_hours
from reminder import balance_reminder
from config import (
    BOT_TOKEN,
    TELEGRAM_CHAT_ID,
    CONTRIBUTION_AMOUNT,
    PAYMENT_URL,
)


dp = Dispatcher()


@dp.message(CommandStart())
async def start_handler(message: Message):
    await message.answer("Этот бот следит за оплатой сервера Selectel.")


@dp.message(Command("chat_id"))
async def chat_id_handler(message: Message):
    await message.answer(f"ID этого чата: {message.chat.id}")


@dp.message(Command("status"))
async def status_handler(message: Message):
    """Проверяет прогнозируемое количество часов до окончания баланса Selectel.

    Отправляет сообщение с результатом в чат по запросу.
    """
    if message.chat.id != TELEGRAM_CHAT_ID:
        return

    try:
        hours = await get_forecast_hours()
    except httpx.HTTPError as error:
        print(f"Ошибка Selectel API: {error}")
        await message.answer("Не удалось получить данные Selectel.")
        return
    except (KeyError, TypeError, ValueError) as error:
        print(f"Неожиданный ответ Selectel: {error}")
        await message.answer("Selectel вернул данные в неожиданном формате.")
        return

    if hours < 24:
        remaining = f"{hours:.0f} ч."
    else:
        remaining = f"{hours / 24:.1f} дн."

    await message.answer(
        f"Сервер Selectel\n"
        f"Баланс рассчитан примерно на: {remaining}"
    )


@dp.message(Command("pay"))
async def pay_handler(message: Message):
    """Отправляет сообщение с кнопкой для перевода средств на Selectel."""
    if message.chat.id != TELEGRAM_CHAT_ID:
        return

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=f"Перевести ({CONTRIBUTION_AMOUNT} руб.)",
                    url=PAYMENT_URL,
                )
            ]
        ]
    )

    await message.answer(
        "Сбор на оплату сервера Selectel (на Сбер)",
        reply_markup=keyboard,
    )


async def main():
    bot = Bot(token=BOT_TOKEN)
    asyncio.create_task(balance_reminder(bot))
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
