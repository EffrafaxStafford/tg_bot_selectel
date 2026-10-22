import os
import httpx
from dotenv import load_dotenv

load_dotenv()

SELECTEL_TOKEN_TYPE = os.getenv("SELECTEL_TOKEN_TYPE", "static").lower()
SELECTEL_TOKEN = os.getenv("SELECTEL_TOKEN")
SELECTEL_BALANCE = os.getenv("SELECTEL_BALANCE", "primary")
SELECTEL_API_URL = os.getenv("SELECTEL_API_URL")


if SELECTEL_TOKEN_TYPE not in {"static", "iam"}:
    raise RuntimeError("SELECTEL_TOKEN_TYPE должен быть static или iam")
if not SELECTEL_TOKEN:
    raise RuntimeError("В .env не указан SELECTEL_TOKEN")
if not SELECTEL_API_URL:
    raise RuntimeError("В .env не указан SELECTEL_API_URL")


async def get_forecast_hours() -> float:
    """Получает прогнозируемое количество часов до окончания баланса Selectel."""

    if SELECTEL_TOKEN_TYPE == "iam":
        headers = {"X-Auth-Token": SELECTEL_TOKEN}
    else:
        headers = {"X-Token": SELECTEL_TOKEN}

    async with httpx.AsyncClient(timeout=10) as client:
        response = await client.get(
            SELECTEL_API_URL,
            headers=headers,
        )
        response.raise_for_status()

    data = response.json()
    hours = data["data"].get(SELECTEL_BALANCE)

    if hours is None:
        raise ValueError(
            f"Для баланса {SELECTEL_BALANCE} прогноз недоступен"
        )

    return float(hours)
