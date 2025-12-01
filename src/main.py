"""メインエントリーポイント"""

import logging
import sys
from datetime import datetime

from src.config import config
from src.database import SessionLocal
from src.downloader import StockDownloader
from src.stock_list import get_stock_list

# ログ設定
logging.basicConfig(
    level=getattr(logging, config.log_level),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger(__name__)


def daily_download_job():
    """日次株価ダウンロードジョブ（当日分のみ）"""
    logger.info("Starting daily stock price download job")
    start_time = datetime.now()

    db = SessionLocal()
    try:
        downloader = StockDownloader(db, batch_size=config.download_batch_size)

        stock_list = get_stock_list()
        logger.info(f"Downloading daily prices for {len(stock_list)} stocks")

        saved_count = downloader.download_daily_prices(stock_list)

        elapsed = datetime.now() - start_time
        logger.info(f"Daily download completed: {saved_count} records saved in {elapsed}")

    except Exception as e:
        logger.error(f"Error in daily download job: {e}", exc_info=True)
        raise
    finally:
        db.close()


def main():
    """メイン関数 - 日次ダウンロードを1回実行"""
    logger.info("Stock Downloader started")
    daily_download_job()
    logger.info("Stock Downloader finished")


if __name__ == "__main__":
    main()
