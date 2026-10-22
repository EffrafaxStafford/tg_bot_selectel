from aiogram import Bot
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from collection import get_collection, start_collection
from config import CONTRIBUTION_AMOUNT, PAYMENT_URL


def format_collection_text(collection: dict) -> str:
    paid_names = list(collection["paid"].values())

    if paid_names:
        paid_list = "\n".join(
            f"{number}. {name}"
            for number, name in enumerate(paid_names, start=1)
        )
    else:
        paid_list = "Пока никто не отметил оплату."

    return (
        "Сбор на оплату сервера Selectel\n"
        f"Отметили оплату:\n{paid_list}"
    )


def create_collection_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=f"Перевести ({CONTRIBUTION_AMOUNT} руб.)",
                    url=PAYMENT_URL,
                )
            ],
            [
                InlineKeyboardButton(
                    text="✅ Я оплатил",
                    callback_data="toggle_payment",
                )
            ],
        ]
    )


async def send_collection(bot: Bot, chat_id: int) -> int:
    """Отправляет сбор, если активного сбора ещё нет."""

    collection = get_collection()

    if collection["active"]:
        return collection["message_id"]

    message = await bot.send_message(
        chat_id=chat_id,
        text=format_collection_text(collection),
        reply_markup=create_collection_keyboard(),
    )

    start_collection(message.message_id)
    return message.message_id
