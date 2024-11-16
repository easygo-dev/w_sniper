import json
import sys
from pathlib import Path
from loguru import logger

# Создаем директорию для логов если её нет
log_path = Path("data/logs")
log_path.mkdir(parents=True, exist_ok=True)

# Удаляем стандартный обработчик
logger.remove()

# Добавляем логирование в консоль
logger.add(
    sys.stderr,
    format="<white>{time:HH:mm:ss}</white> | <level>{message}</level>",
    level="INFO"
)

# Добавляем логирование в файл с ротацией
logger.add(
    "data/logs/volume_buyer_{time:YYYY-MM-DD}.log",
    rotation="00:00",  # Новый файл каждый день
    retention="7 days",  # Хранить логи за последние 7 дней
    compression="zip",  # Сжимать старые логи
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
    level="INFO",
    encoding="utf-8"
)

# Network data
CHAIN_DATA = {
    "base": {
        "rpc": "https://mainnet.base.org",
        "explorer": "https://basescan.org",
        "token": "ETH",
        "chain_id": 8453,
    },
}

# Load ABI
with open("data/abi/erc20.json") as f:
    ERC20_ABI = json.load(f)

# Zero address constant
ZERO_ADDRESS = "0x0000000000000000000000000000000000000000"