from eth_account import Account
from web3 import Web3

import settings
from modules.config import CHAIN_DATA, ERC20_ABI, logger
from modules.utils import random_sleep

class Wallet:
    def __init__(self, private_key, counter=None, chain="base"):
        self.private_key = private_key
        self.account = Account.from_key(private_key)
        self.address = self.account.address

        self.chain = chain
        self.w3 = Web3(Web3.HTTPProvider(CHAIN_DATA[chain]["rpc"]))
        self.explorer = CHAIN_DATA[chain]["explorer"]

        self.counter = counter
        self.label = f"{self.counter} {self.address} | "

    def get_balance(self, token_addr=None):
        if token_addr == None:
            balance = self.w3.eth.get_balance(self.address)
        else:
            token = self.get_contract(token_addr)
            balance = token.functions.balanceOf(self.address).call()
        return balance

    def get_contract(self, address, abi=None):
        contract_address = self.w3.to_checksum_address(address)
        if not abi:
            abi = ERC20_ABI
        return self.w3.eth.contract(address=contract_address, abi=abi)

    def get_tx_data(self, value=0, **kwargs):
        return {
            "chainId": self.w3.eth.chain_id,
            "from": self.address,
            "nonce": self.w3.eth.get_transaction_count(self.address),
            "value": value,
            **kwargs,
        }

    def send_tx(self, tx, tx_label="", retry=0):
        try:
            if retry > 0:
                tx["nonce"] = self.w3.eth.get_transaction_count(self.address)

            signed_tx = self.w3.eth.account.sign_transaction(tx, self.private_key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
            logger.info(f"{tx_label} | {self.explorer}/tx/{tx_hash.hex()}")

            tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            
            attempts = f"after {retry + 1} attempts" if retry > 0 else ""

            if tx_receipt["status"] == 1:
                logger.success(f"{tx_label} | Tx confirmed {attempts}\n")
                return tx_receipt
            else:
                raise Exception(f"{tx_label} | Tx Failed\n")

        except Exception as error:
            logger.error(f"{tx_label} | {error}\n")
            if retry < settings.RETRY_COUNT:
                random_sleep(*settings.SLEEP_BETWEEN_ACTIONS)
                return self.send_tx(tx, tx_label, retry=retry + 1)
            return None