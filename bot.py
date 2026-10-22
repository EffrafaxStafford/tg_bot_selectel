import asyncio
import httpx

from aiogram.filters import Command, CommandStart
from aiogram import Bot, Dispatcher, F
from aiogram.types import CallbackQuery, Message
from selectel import get_forecast_hours
from reminder import balance_reminder
from collection import (
    get_collection,
    reset_collection,
    toggle_payment,
)
from collection_message import format_collection_text, send_collection
from config import (
    BOT_TOKEN,
    TELEGRAM_CHAT_ID,
    TELEGRAM_OWNER_ID,
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
    if message.chat.id != TELEGRAM_CHAT_ID:
        return

    collection = get_collection()

    if not collection["active"]:
        await message.answer(
            "Активного сбора сейчас нет."
        )
        return

    await message.answer(
        "Актуальный сбор в сообщении выше.",
        reply_to_message_id=collection["message_id"],
        allow_sending_without_reply=True,
    )


@dp.callback_query(F.data == "toggle_payment")
async def payment_callback(callback: CallbackQuery):
    if callback.message is None:
        await callback.answer()
        return

    collection = get_collection()

    if (
        not collection["active"]
        or callback.message.message_id != collection["message_id"]
    ):
        await callback.answer(
            "Этот сбор уже неактивен.",
            show_alert=True,
        )
        return

    is_paid = toggle_payment(
        user_id=callback.from_user.id,
        name=callback.from_user.full_name,
    )

    collection = get_collection()

    if is_paid:
        await callback.answer("Оплата отмечена")
    else:
        await callback.answer("Отметка снята")

    await callback.message.edit_text(
        format_collection_text(collection),
        reply_markup=callback.message.reply_markup,
    )


@dp.message(Command("new_collection"))
async def new_collection_handler(message: Message):
    if (
        message.chat.id != TELEGRAM_CHAT_ID
        or message.from_user is None
    ):
        return

    if message.from_user.id != TELEGRAM_OWNER_ID:
        await message.answer(
            "Создать новый сбор может только владелец бота."
        )
        return

    reset_collection()

    await send_collection(
        bot=message.bot,
        chat_id=message.chat.id,
    )


async def main():
    bot = Bot(token=BOT_TOKEN)
    asyncio.create_task(balance_reminder(bot))
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
