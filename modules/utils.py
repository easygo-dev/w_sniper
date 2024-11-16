import json
import os
import random
import time
from datetime import datetime, timedelta
from typing import Dict, List

import requests
from tqdm import tqdm
from web3 import Web3

import settings
from modules.config import logger

def wei(amount_eth: float) -> int:
    return Web3.to_wei(amount_eth, "ether")

def ether(amount_wei: int) -> float:
    return Web3.from_wei(amount_wei, "ether")

def get_eth_price(symbol="ETH") -> float:
    url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}USDT"
    response = requests.get(url)
    data = response.json()
    return float(data["price"])

def get_coins(json_path: str) -> None:
    """Fetches coin data from wow.xyz and writes to a json file"""
    json_data = {
        "query": """
        query TokensQuery($sortType: WowTrendingType!, $chainName: EChainName!, $order: SortingOrder!) {
          wowTrending(
            trendingType: $sortType
            chainName: $chainName
            first: 100
            order: $order
          ) {
            edges {
              node {
                name
                symbol
                address
                usdPrice
                marketCap
                totalSupply
                description
                getMarketStats {
                  volume
                }
                creator {
                  walletAddress
                  handle
                }
                trades {
                  edges {
                    node {
                      timestamp
                      usdPrice
                    }
                  }
                }
              }
            }
          }
        }
        """,
        "variables": {
            "sortType": "MARKETCAP",
            "chainName": "BaseMainnet",
            "order": "DESC"
        }
    }

    resp = requests.post(
        "https://api.wow.xyz/universal/graphql",
        json=json_data,
        headers={
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0"
        }
    )

    if resp.status_code != 200:
        logger.error(f"HTTP Error: {resp.status_code} {resp.text}")
        return None

    data = resp.json()["data"]["wowTrending"]["edges"]
    
    with open(json_path, "w") as file:
        json.dump(data, file, indent=4)

def fetch_data(*, update: bool = False, json_path: str = "data/trending.json") -> List[Dict]:
    """Fetches data either from a local JSON cache file or from a remote API"""
    if update:
        json_data = None
    else:
        try:
            # Retrieve last modified time of the cache file
            file_stat = os.stat(json_path)
            last_modified_time = datetime.fromtimestamp(file_stat.st_mtime)
            current_time = datetime.now()
            
            time_difference = current_time - last_modified_time
            max_age = timedelta(minutes=settings.CACHE_MAX_AGE)

            # Check if cache is still valid
            if time_difference < max_age:
                with open(json_path, "r") as f:
                    json_data = json.load(f)
                    logger.info("Using data from local JSON cache\n")
            else:
                logger.info("Local cache is outdated...")
                json_data = None

        except FileNotFoundError:
            logger.info("No local cache found...")
            json_data = None

    # If no cache found, fetch the data from remote source
    if not json_data:
        logger.info("Fetching data from remote API\n")
        get_coins(json_path)
        # Load the newly fetched data
        with open(json_path, "r") as f:
            json_data = json.load(f)

    return json_data

def random_sleep(from_sleep: int, to_sleep: int) -> None:
    x = random.randint(from_sleep, to_sleep)
    time.sleep(x)

def sleep(from_sleep: int, to_sleep: int) -> None:
    x = random.randint(from_sleep, to_sleep)
    desc = datetime.now().strftime("%H:%M:%S")

    for _ in tqdm(
        range(x), desc=desc, bar_format="{desc} | Sleeping {n_fmt}/{total_fmt}"
    ):
        time.sleep(1)
    print()