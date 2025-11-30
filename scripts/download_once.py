#!/usr/bin/env python3
"""一度だけ株価をダウンロードするスクリプト"""

import logging
import sys
from datetime import datetime

# srcディレクトリをパスに追加
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
    logger.info("Starting one-time stock price download")
    start_time = datetime.now()

    db = SessionLocal()
    try:
        downloader = StockDownloader(db, batch_size=config.download_batch_size)

        stock_list = get_stock_list()
        logger.info(f"Downloading prices for {len(stock_list)} stocks")

        saved_count = downloader.download_stock_prices(stock_list)

        elapsed = datetime.now() - start_time
        logger.info(f"Download completed: {saved_count} records saved in {elapsed}")

    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    main()
