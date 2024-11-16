import os
from dotenv import load_dotenv

load_dotenv()

# WOW.xyz settings
MIN_VOLUME_USD = float(os.getenv("MIN_VOLUME_USD", "30.0"))  # Минимальный объем для покупки
BUY_AMOUNT_ETH = float(os.getenv("BUY_AMOUNT_ETH", "0.007"))  # Сумма покупки в ETH
CACHE_MAX_AGE = 5  # 5 min

# Network settings
RPC_URL = os.getenv("RPC_URL", "https://mainnet.base.org")
CHAIN_ID = 8453  # Base Network

# Account management
SLEEP_BETWEEN_WALLETS = [5, 10]
SLEEP_BETWEEN_ACTIONS = [5, 10]
SHUFFLE_KEYS = False
RETRY_COUNT = 3  # Количество попыток для повторной отправки транзакции
SCAN_INTERVAL = 60  # Интервал между сканированиями в секундах

# Telegram settings
TELEGRAM_ENABLED = bool(os.getenv("TELEGRAM_ENABLED", "True"))
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# File paths
HISTORY_FILE = "data/bought.json"

# Gas settings
GAS_LIMIT = 500000  # 500k gas
GAS_PRICE_MULTIPLIER = 1.2  # Увеличение на 20% при повторной попытке