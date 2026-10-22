import asyncio
import os
import httpx

from aiogram import Bot, Dispatcher
from aiogram.filters import Command, CommandStart
from aiogram.types import Message
from dotenv import load_dotenv

from selectel import get_forecast_hours


load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = int(os.getenv("TELEGRAM_CHAT_ID"))
WARNING_THRESHOLDS_HOURS = [int(x) for x in os.getenv(
    "WARNING_THRESHOLDS_HOURS", "168,72,24,6").split(",")]

last_sent_threshold = None

if not BOT_TOKEN:
    raise RuntimeError("В .env не указан TELEGRAM_BOT_TOKEN")


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


async def balance_reminder(bot: Bot):
    """Отправляет сообщение в чат, если баланс заканчивается."""
    global last_sent_threshold
    while True:
        try:
            hours = await get_forecast_hours()

            current_threshold = min(
                (
                    threshold
                    for threshold in WARNING_THRESHOLDS_HOURS
                    if hours <= threshold
                ),
                default=None,
            )

            # Баланса снова хватает больше чем на семь дней
            if current_threshold is None:
                last_sent_threshold = None
            # Прогноз ухудшился и достиг нового порога
            elif (
                last_sent_threshold is None
                or current_threshold < last_sent_threshold
            ):
                await bot.send_message(
                    chat_id=TELEGRAM_CHAT_ID,
                    text=(
                        "Заканчиваются средства на Selectel!\n"
                        f"Их хватит примерно на {hours / 24:.1f} дн."
                    ),
                )

                last_sent_threshold = current_threshold
            # Баланс увеличился, но всё ещё ниже семи дней
            elif current_threshold > last_sent_threshold:
                last_sent_threshold = current_threshold

        except Exception as error:
            print(f"Ошибка проверки баланса: {error}")

        await asyncio.sleep(60 * 60)


async def main():
    bot = Bot(token=BOT_TOKEN)
    asyncio.create_task(balance_reminder(bot))
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
