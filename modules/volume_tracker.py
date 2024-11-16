import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Set
from modules.config import logger
from modules.notifications import send_telegram_message
import settings

class VolumeTracker:
    def __init__(self):
        self.history_file = settings.HISTORY_FILE
        Path(self.history_file).parent.mkdir(parents=True, exist_ok=True)
        self.bought_tokens = self.load_bought_tokens()
        logger.info(f"Loaded {len(self.bought_tokens)} previously bought tokens")

    def load_bought_tokens(self) -> Set[str]:
        """Load previously bought tokens"""
        try:
            with open(self.history_file, 'r') as f:
                data = json.load(f)
                return set(data.keys())
        except FileNotFoundError:
            return set()

    def save_bought_token(self, token_data: Dict, tx_hash: str):
        """Save bought token info"""
        try:
            with open(self.history_file, 'r') as f:
                data = json.load(f)
        except FileNotFoundError:
            data = {}

        data[token_data['address']] = {
            'symbol': token_data['symbol'],
            'name': token_data['name'],
            'buy_price_usd': token_data['usdPrice'],
            'buy_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'volume_at_buy': token_data['volume'],
            'tx_hash': tx_hash
        }

        with open(self.history_file, 'w') as f:
            json.dump(data, f, indent=2)

    def check_volume(self, token_data: Dict) -> bool:
        """Check if token meets volume criteria"""
        try:
            symbol = token_data['symbol']
            volume = float(token_data.get('getMarketStats', {}).get('volume', '0'))
            address = token_data['address']
            
            logger.debug(
                f"Checking {symbol} ({address}): "
                f"Volume=${volume:.2f}, "
                f"Min Required=${settings.MIN_VOLUME_USD}"
            )

            if address in self.bought_tokens:
                logger.debug(f"Skipping {symbol}: already bought")
                return False

            if volume >= settings.MIN_VOLUME_USD:
                msg = (
                    f"🔍 Found token with sufficient volume:\n"
                    f"Symbol: {symbol}\n"
                    f"Contract: {address}\n"
                    f"Volume: ${volume:.2f}\n"
                    f"Price: ${float(token_data['usdPrice']):.8f}"
                )
                logger.info(msg)
                if settings.TELEGRAM_ENABLED:
                    send_telegram_message(msg)
                return True
                
            return False
        except Exception as e:
            logger.error(f"Error checking volume for {token_data.get('symbol', 'Unknown')}: {e}")
            return False