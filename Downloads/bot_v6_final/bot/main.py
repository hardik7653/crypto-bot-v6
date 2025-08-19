import sys

import os

# ✅ Add parent directory (D:/projects) to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bot.data.data_processor import add_indicators
from bot.execution.exchange_connector import ExchangeConnector
from bot.strategies.ml_strategy import MLStrategy
from bot.utils.logging import logger


def main():
    logger.info("Starting trading bot...")

    # Initialize exchange connector
    connector = ExchangeConnector("binance", use_testnet=True)

    # Fetch balance
    bal = connector.fetch_balance()
    logger.info(f"Balance: {bal}")

    # Run ML Strategy
    ml_strategy = MLStrategy()
    ml_strategy.run()


if __name__ == "__main__":
    main()
