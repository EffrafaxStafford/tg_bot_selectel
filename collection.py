import json
from pathlib import Path


DATA_FILE = Path(__file__).parent / "data" / "collection.json"


def empty_collection() -> dict:
    """Возвращает пустое состояние сбора."""
    return {
        "active": False,
        "message_id": None,
        "paid": {},
    }


def get_collection() -> dict:
    """Загружает текущий сбор из файла."""
    if not DATA_FILE.exists():
        return empty_collection()

    return json.loads(DATA_FILE.read_text(encoding="utf-8"))


def save_collection(collection: dict) -> None:
    """Сохраняет состояние сбора."""
    DATA_FILE.parent.mkdir(exist_ok=True)

    DATA_FILE.write_text(
        json.dumps(collection, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def start_collection(message_id: int) -> None:
    """Создаёт новый активный сбор."""
    collection = empty_collection()
    collection["active"] = True
    collection["message_id"] = message_id
    save_collection(collection)


def toggle_payment(user_id: int, name: str) -> bool:
    """Добавляет или снимает отметку об оплате."""

    collection = get_collection()
    user_id = str(user_id)

    if user_id in collection["paid"]:
        del collection["paid"][user_id]
        is_paid = False
    else:
        collection["paid"][user_id] = name
        is_paid = True

    save_collection(collection)
    return is_paid


def reset_collection() -> None:
    """Удаляет состояние предыдущего сбора."""
    save_collection(empty_collection())
