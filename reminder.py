import asyncio

from aiogram import Bot

from selectel import get_forecast_hours
from config import (
    WARNING_THRESHOLDS_HOURS,
    TELEGRAM_CHAT_ID,
)
from collection import get_collection, reset_collection
from collection_message import send_collection


last_sent_threshold = None


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

                # Предыдущий сбор больше неактивен
                collection = get_collection()
                if collection["active"]:
                    reset_collection()

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

                # Создаём сбор после первого предупреждения
                collection = get_collection()
                if not collection["active"]:
                    await send_collection(
                        bot=bot,
                        chat_id=TELEGRAM_CHAT_ID,
                    )

                last_sent_threshold = current_threshold

            # Баланс увеличился, но всё ещё ниже семи дней
            elif current_threshold > last_sent_threshold:
                last_sent_threshold = current_threshold

        except Exception as error:
            print(f"Ошибка проверки баланса: {error}")

        await asyncio.sleep(60 * 60)
