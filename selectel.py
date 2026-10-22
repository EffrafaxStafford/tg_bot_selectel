import httpx

from config import (
    SELECTEL_TOKEN_TYPE,
    SELECTEL_TOKEN,
    SELECTEL_BALANCE,
    SELECTEL_API_URL,
)


last_sent_threshold = None


async def get_forecast_hours() -> float:
    """Получает прогнозируемое количество часов
    до окончания баланса Selectel.
    """

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
