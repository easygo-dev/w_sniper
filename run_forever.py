import sys
import time
from datetime import datetime
import signal
from pathlib import Path
from loguru import logger
import settings
from modules.notifications import send_telegram_message
from main import main as volume_buyer_main

def signal_handler(signum, frame):
    """Обработчик сигналов для graceful shutdown"""
    logger.warning("Received shutdown signal. Finishing current iteration...")
    if settings.TELEGRAM_ENABLED:
        send_telegram_message("⚠️ Bot is shutting down...")
    sys.exit(0)

def run_forever():
    # Регистрируем обработчик сигналов
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    logger.info("Starting volume buyer bot in continuous mode")
    if settings.TELEGRAM_ENABLED:
        send_telegram_message("🤖 Volume buyer bot started in continuous mode")

    iteration = 1
    while True:
        try:
            start_time = datetime.now()
            logger.info(f"Starting iteration {iteration}")
            
            # Запускаем основной скрипт
            volume_buyer_main()
            
            duration = (datetime.now() - start_time).total_seconds()
            logger.info(
                f"Iteration {iteration} completed in {duration:.1f} seconds. "
                f"Waiting {settings.SCAN_INTERVAL} seconds before next scan..."
            )
            
            iteration += 1
            time.sleep(settings.SCAN_INTERVAL)

        except Exception as e:
            logger.error(f"Error in main loop: {e}")
            if settings.TELEGRAM_ENABLED:
                send_telegram_message(f"❌ Error in main loop: {str(e)}")
            time.sleep(60)  # Ждем минуту перед повторной попыткой

if __name__ == "__main__":
    run_forever()