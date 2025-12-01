#!/usr/bin/env python3
"""過去データのテクニカル指標を一括計算するスクリプト"""

import logging
import sys
from datetime import datetime

sys.path.insert(0, "/app")

from src.config import config
from src.database import SessionLocal
from src.downloader import StockDownloader
from src.models import Stock

logging.basicConfig(
    level=getattr(logging, config.log_level),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def main():
    logger.info("Starting backfill: calculating technical indicators for all historical data")
    start_time = datetime.now()

    db = SessionLocal()
    try:
        downloader = StockDownloader(db, batch_size=config.download_batch_size)

        # 全銘柄コードを取得
        stock_codes = [s.code for s in db.query(Stock.code).all()]
        logger.info(f"Calculating indicators for {len(stock_codes)} stocks")

        # 全期間のテクニカル指標を計算（limit_days=0で全期間）
        updated_count = downloader.update_all_indicators(stock_codes, limit_days=0)

        elapsed = datetime.now() - start_time
        logger.info(f"Backfill completed: {updated_count} records updated in {elapsed}")

    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    main()
