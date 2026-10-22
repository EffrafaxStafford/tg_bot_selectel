import os

from dotenv import load_dotenv


load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("В .env не указан TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
if not TELEGRAM_CHAT_ID:
    raise RuntimeError("В .env не указан TELEGRAM_CHAT_ID")
TELEGRAM_CHAT_ID = int(TELEGRAM_CHAT_ID)
TELEGRAM_OWNER_ID = os.getenv("TELEGRAM_OWNER_ID")
if not TELEGRAM_OWNER_ID:
    raise RuntimeError("В .env не указан TELEGRAM_OWNER_ID")
TELEGRAM_OWNER_ID = int(TELEGRAM_OWNER_ID)
TELEGRAM_PROXY_URL = os.getenv("TELEGRAM_PROXY_URL")

SELECTEL_TOKEN_TYPE = os.getenv("SELECTEL_TOKEN_TYPE", "static").lower()
if SELECTEL_TOKEN_TYPE not in {"static", "iam"}:
    raise RuntimeError("SELECTEL_TOKEN_TYPE должен быть static или iam")
SELECTEL_TOKEN = os.getenv("SELECTEL_TOKEN")
if not SELECTEL_TOKEN:
    raise RuntimeError("В .env не указан SELECTEL_TOKEN")
SELECTEL_BALANCE = os.getenv("SELECTEL_BALANCE", "primary")
SELECTEL_API_URL = os.getenv("SELECTEL_API_URL")
if not SELECTEL_API_URL:
    raise RuntimeError("В .env не указан SELECTEL_API_URL")

WARNING_THRESHOLDS_HOURS = [int(x) for x in os.getenv(
    "WARNING_THRESHOLDS_HOURS", "168,72,24").split(",")]

CONTRIBUTION_AMOUNT = int(
    os.getenv("CONTRIBUTION_AMOUNT", "100")
)
PAYMENT_URL = os.getenv("PAYMENT_URL")
if not PAYMENT_URL:
    raise RuntimeError("В .env не указан PAYMENT_URL")
