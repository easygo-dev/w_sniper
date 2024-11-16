import asyncio
from telegram.ext import Application
import settings
from modules.config import logger

async def _send_telegram_message(text: str):
    if not all([settings.TELEGRAM_BOT_TOKEN, settings.TELEGRAM_CHAT_ID]):
        logger.warning("Telegram credentials not provided")
        return

    try:
        app = Application.builder().token(settings.TELEGRAM_BOT_TOKEN).build()
        await app.bot.send_message(
            chat_id=settings.TELEGRAM_CHAT_ID,
            text=text,
            parse_mode='HTML',
            disable_web_page_preview=True
        )
    except Exception as e:
        logger.error(f"Failed to send Telegram notification: {e}")

def send_telegram_message(text: str):
    if settings.TELEGRAM_ENABLED:
        asyncio.run(_send_telegram_message(text))