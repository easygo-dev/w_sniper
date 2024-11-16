import random
import time
from pathlib import Path
from eth_account import Account
from loguru import logger

import settings
from modules.config import logger
from modules.token import Token
from modules.volume_tracker import VolumeTracker
from modules.utils import fetch_data, sleep
from modules.notifications import send_telegram_message

def run(keys):
    volume_tracker = VolumeTracker()
    
    if settings.SHUFFLE_KEYS:
        random.shuffle(keys)
        
    total_keys = len(keys)
    
    while True:  # Бесконечный цикл сканирования
        try:
            # Получаем актуальные данные о токенах
            tokens_data = fetch_data(update=True)
            logger.info(f"Fetched {len(tokens_data)} tokens")
            
            # Проходим по всем кошелькам
            for index, private_key in enumerate(keys, start=1):
                counter = f"[{index}/{total_keys}]"
                address = Account.from_key(private_key).address
                
                logger.info(f"{counter} Processing wallet {address}")
                
                # Проверяем каждый токен для текущего кошелька
                for token_data in tokens_data:
                    token = Token(private_key, counter, token_data['node'])
                    
                    try:
                        tx_status = token.buy()
                        if tx_status:
                            sleep(*settings.SLEEP_BETWEEN_ACTIONS)
                    except Exception as error:
                        logger.error(f"{counter} {address} | Error processing token: {error}\n")
                
                sleep(*settings.SLEEP_BETWEEN_WALLETS)
                
            logger.info(f"Completed scan iteration, waiting {settings.SCAN_INTERVAL} seconds")
            time.sleep(settings.SCAN_INTERVAL)
            
        except Exception as error:
            logger.error(f"Error in main loop: {error}")
            time.sleep(settings.SLEEP_BETWEEN_ACTIONS[0])

def main():
    # Создаем необходимые директории
    Path("data/logs").mkdir(parents=True, exist_ok=True)
    
    # Загружаем приватные ключи
    with open("keys.txt") as file:
        keys = [row.strip() for row in file]
        
    if settings.TELEGRAM_ENABLED:
        send_telegram_message("🤖 Volume buyer bot started")
    
    try:
        run(keys)
    except KeyboardInterrupt:
        logger.warning("Cancelled by user")
        if settings.TELEGRAM_ENABLED:
            send_telegram_message("⚠️ Bot stopped by user")
    except Exception as e:
        logger.error(f"Critical error: {e}")
        if settings.TELEGRAM_ENABLED:
            send_telegram_message(f"🚨 Critical error: {str(e)}")
        raise

if __name__ == "__main__":
    main()