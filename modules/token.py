from modules.wallet import Wallet
from modules.volume_tracker import VolumeTracker
from modules.notifications import send_telegram_message
from modules.utils import wei, ether, get_eth_price
from modules.config import logger, ZERO_ADDRESS
import settings

class Token(Wallet):
    def __init__(self, private_key, counter, coin_data):
        super().__init__(private_key, counter)
        self.coin = coin_data
        self.label += f"${self.coin['symbol'].upper()} |"
        self.volume_tracker = VolumeTracker()
        
        # Инициализация контракта и параметров
        self.contract = self.get_contract(self.coin['address'])
        self.min_size = self.contract.functions.MIN_ORDER_SIZE().call()
        self.decimals = self.contract.functions.decimals().call()
        self.market_type = self.contract.functions.marketType().call()

    def calc_token_amount(self, amount_usd, slippage=0.05):
        """Calculates the token amount to purchase, accounting for slippage"""
        token_amount = (amount_usd / float(self.coin['usdPrice'])) * (10**self.decimals)
        token_amount_w_slippage = int(token_amount * (1 - slippage))
        return token_amount_w_slippage

    def calc_wei_amount(self, amount_usd):
        eth_price = get_eth_price()
        amount_wei = wei(amount_usd / eth_price)
        return amount_wei

    def buy(self):
        """Buy token if it meets volume criteria"""
        try:
            volume = float(self.coin.get('getMarketStats', {}).get('volume', '0'))
            
            if volume >= settings.MIN_VOLUME_USD:
                # Уведомление о найденном токене
                found_msg = (
                    f"🔍 Found token with sufficient volume:\n"
                    f"Symbol: {self.coin['symbol']}\n"
                    f"Name: {self.coin.get('name', 'N/A')}\n"
                    f"Contract: {self.coin['address']}\n"
                    f"Volume: ${volume:.2f}\n"
                    f"Price: ${float(self.coin['usdPrice']):.8f}"
                )
                logger.info(found_msg)
                if settings.TELEGRAM_ENABLED:
                    send_telegram_message(found_msg)
    
                if self.coin['address'] in self.volume_tracker.bought_tokens:
                    return False
    
                # Далее логика покупки...
                wei_amount = wei(settings.BUY_AMOUNT_ETH)
                if wei_amount >= self.get_balance():
                    logger.warning(
                        f"{self.label} Amount {ether(wei_amount):.6f} ETH exceeds wallet balance, skipping\n"
                    )
                    return False
    
                token_amount = self.calc_token_amount(float(self.coin['usdPrice']) * settings.BUY_AMOUNT_ETH)
                order_size = max(token_amount, self.min_size)
    
                contract_tx = self.contract.functions.buy(
                    self.address,
                    self.address,
                    ZERO_ADDRESS,
                    "",
                    self.market_type,
                    order_size,
                    0,
                ).build_transaction(self.get_tx_data(value=wei_amount))
    
                tx_receipt = self.send_tx(
                    contract_tx,
                    tx_label=f"{self.label} buy",
                )
    
                if tx_receipt:
                    token_info = {
                        'address': self.coin['address'],
                        'symbol': self.coin['symbol'],
                        'name': self.coin.get('name', ''),
                        'usdPrice': self.coin['usdPrice'],
                        'volume': volume,
                    }
                    self.volume_tracker.save_bought_token(token_info, tx_receipt['transactionHash'].hex())
                    
                    # Уведомление об успешной покупке
                    buy_msg = (
                        f"✅ Successfully bought token:\n"
                        f"Symbol: {self.coin['symbol']}\n"
                        f"Contract: {self.coin['address']}\n"
                        f"Amount: {settings.BUY_AMOUNT_ETH} ETH\n"
                        f"Volume: ${volume:.2f}\n"
                        f"Price: ${float(self.coin['usdPrice']):.8f}\n"
                        f"TX: {tx_receipt['transactionHash'].hex()}"
                    )
                    logger.success(buy_msg)
                    if settings.TELEGRAM_ENABLED:
                        send_telegram_message(buy_msg)
                    return True
    
                return False
    
            return False
    
        except Exception as e:
            error_msg = f"Error buying {self.coin['symbol']}: {str(e)}"
            logger.error(error_msg)
            if settings.TELEGRAM_ENABLED:
                send_telegram_message(f"❌ {error_msg}")
            return False