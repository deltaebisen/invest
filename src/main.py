"""メインエントリーポイント"""

import logging
import os
import sys
import time
from datetime import datetime

import schedule

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
        logging.FileHandler("/app/logs/stock_downloader.log", mode="a"),
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
    finally:
        db.close()


def main():
    """メイン関数"""
    logger.info("Stock Downloader started (daily update mode)")

    # 起動時に即座に実行するかどうか（環境変数で制御）
    if os.getenv("RUN_ON_STARTUP", "false").lower() == "true":
        logger.info("Running initial download on startup")
        daily_download_job()

    # 毎日18:00に実行（東証終了後）
    schedule.every().day.at("18:00").do(daily_download_job)

    logger.info("Scheduler started. Running daily at 18:00 JST")

    while True:
        schedule.run_pending()
        time.sleep(60)


if __name__ == "__main__":
    main()
