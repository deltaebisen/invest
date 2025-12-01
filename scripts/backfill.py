#!/usr/bin/env python3
"""過去1年分の株価データを一括取得するスクリプト"""

import logging
import sys
from datetime import datetime, timedelta

sys.path.insert(0, "/app")

from src.config import config
from src.database import SessionLocal
from src.downloader import StockDownloader
from src.stock_list import get_stock_list

logging.basicConfig(
    level=getattr(logging, config.log_level),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def main():
    logger.info("Starting backfill: downloading 1 year of historical data")
    start_time = datetime.now()

    # 1年前から今日まで
    end_date = datetime.now() + timedelta(days=1)
    start_date = end_date - timedelta(days=365)

    db = SessionLocal()
    try:
        downloader = StockDownloader(db, batch_size=config.download_batch_size)

        stock_list = get_stock_list()
        logger.info(f"Downloading historical prices for {len(stock_list)} stocks")
        logger.info(f"Period: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")

        saved_count = downloader.download_stock_prices(
            stock_list, start_date=start_date, end_date=end_date
        )

        elapsed = datetime.now() - start_time
        logger.info(f"Backfill completed: {saved_count} records saved in {elapsed}")

    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    main()
