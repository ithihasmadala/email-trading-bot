'''
This script is used to track open positions and close them based on take profit and stop loss conditions.
'''

import os
import time

import logging
from binance.um_futures import UMFutures
from binance.lib.utils import config_logging
from binance.error import ClientError
from dotenv import load_dotenv

from utils import create_futures_order
load_dotenv()

config_logging(logging, logging.INFO)

# HMAC authentication with API key and secret
KEY = os.getenv('TESTNET_API_KEY')
SECRET = os.getenv('TESTNET_API_SECRET')
TAKE_PROFIT = float(os.getenv('TAKE_PROFIT'))
STOP_LOSS = float(os.getenv('STOP_LOSS'))
POLLING_INTERVAL = int(os.getenv('POLLING_INTERVAL'))

hmac_client = UMFutures(key=KEY, secret=SECRET, base_url=os.getenv('TESTNET_URL'))

def check_positions():
    try:
        positions = hmac_client.get_position_risk()
        logging.info(f"Positions: {positions}")
        for position in positions:
            symbol = position['symbol']
            entry_price = float(position['entryPrice'])
            current_price = float(position['markPrice'])
            position_amt = float(position['positionAmt'])

            if position_amt > 0:  # Long position
                if current_price >= entry_price * (1 + TAKE_PROFIT):
                    logging.info(f"Take profit reached for {symbol}. Closing long position.")
                    create_futures_order(symbol, 'SELL')
                elif current_price <= entry_price * (1 - STOP_LOSS):
                    logging.info(f"Stop loss reached for {symbol}. Closing long position.")
                    create_futures_order(symbol, 'SELL')
            elif position_amt < 0:  # Short position
                if current_price <= entry_price * (1 - TAKE_PROFIT):
                    logging.info(f"Take profit reached for {symbol}. Closing short position.")
                    create_futures_order(symbol, 'BUY')
                elif current_price >= entry_price * (1 + STOP_LOSS):
                    logging.info(f"Stop loss reached for {symbol}. Closing short position.")
                    create_futures_order(symbol, 'BUY')
    except ClientError as e:
        logging.error(f"Error fetching positions: {e.error_message}")

def __main():
    while True:
        check_positions()
        time.sleep(POLLING_INTERVAL)  # Check periodically

if(__name__ == "__main__"):
    __main()