"""株価データをダウンロードするモジュール"""

import logging
import time
from datetime import datetime, timedelta

import pandas as pd
import yfinance as yf
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from src.models import Stock, StockPrice
from src.stock_list import StockInfo, get_yahoo_ticker

logger = logging.getLogger(__name__)

# バッチ間の待機時間（秒）- レート制限対策
BATCH_DELAY_SECONDS = 2


class StockDownloader:
    def __init__(self, db: Session, batch_size: int = 50):
        self.db = db
        self.batch_size = batch_size

    def download_stock_prices(
        self,
        stock_list: list[StockInfo],
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> int:
        """
        株価データをダウンロードしてDBに保存する

        Args:
            stock_list: 銘柄リスト
            start_date: 開始日（デフォルト: 1年前）
            end_date: 終了日（デフォルト: 今日）

        Returns:
            保存したレコード数
        """
        if start_date is None:
            start_date = datetime.now() - timedelta(days=365)
        if end_date is None:
            end_date = datetime.now()

        total_saved = 0

        # バッチ処理
        for i in range(0, len(stock_list), self.batch_size):
            batch = stock_list[i : i + self.batch_size]
            logger.info(
                f"Processing batch {i // self.batch_size + 1}"
                f" ({len(batch)} stocks, {i + 1}-{i + len(batch)}/{len(stock_list)})"
            )

            # 銘柄マスタを更新
            self._upsert_stocks(batch)

            # 株価データをダウンロード
            saved = self._download_batch(batch, start_date, end_date)
            total_saved += saved

            logger.info(f"Batch completed: {saved} records saved")

            # レート制限対策で少し待機
            if i + self.batch_size < len(stock_list):
                time.sleep(BATCH_DELAY_SECONDS)

        return total_saved

    def _upsert_stocks(self, stocks: list[StockInfo]) -> None:
        """銘柄マスタをupsertする"""
        for stock in stocks:
            stmt = insert(Stock).values(
                code=stock.code,
                name=stock.name,
                market=stock.market,
                sector=stock.sector if hasattr(stock, "sector") else None,
            )
            stmt = stmt.on_conflict_do_update(
                index_elements=["code"],
                set_={
                    "name": stock.name,
                    "market": stock.market,
                    "sector": stock.sector if hasattr(stock, "sector") else None,
                    "updated_at": datetime.utcnow(),
                },
            )
            self.db.execute(stmt)
        self.db.commit()

    def _download_batch(
        self, stocks: list[StockInfo], start_date: datetime, end_date: datetime
    ) -> int:
        """バッチで株価データをダウンロードする"""
        tickers = [get_yahoo_ticker(s.code) for s in stocks]
        ticker_to_code = {get_yahoo_ticker(s.code): s.code for s in stocks}

        try:
            # yfinanceでまとめてダウンロード
            data = yf.download(
                tickers,
                start=start_date.strftime("%Y-%m-%d"),
                end=end_date.strftime("%Y-%m-%d"),
                group_by="ticker",
                auto_adjust=False,
                progress=False,
            )

            if data.empty:
                logger.warning("No data downloaded")
                return 0

            return self._save_price_data(data, ticker_to_code, tickers)

        except Exception as e:
            logger.error(f"Error downloading data: {e}")
            return 0

    def _save_price_data(
        self, data: pd.DataFrame, ticker_to_code: dict[str, str], tickers: list[str]
    ) -> int:
        """株価データをDBに保存する"""
        saved_count = 0

        # 単一銘柄の場合はカラム構造が異なる
        if len(tickers) == 1:
            ticker = tickers[0]
            code = ticker_to_code[ticker]
            saved_count += self._save_single_ticker(data, code)
        else:
            # 複数銘柄の場合
            for ticker in tickers:
                if ticker not in data.columns.get_level_values(0):
                    continue
                ticker_data = data[ticker]
                code = ticker_to_code[ticker]
                saved_count += self._save_single_ticker(ticker_data, code)

        return saved_count

    def _to_float(self, value) -> float | None:
        """numpy/pandas型をPython floatに変換"""
        if pd.isna(value):
            return None
        return float(value)

    def _to_int(self, value) -> int | None:
        """numpy/pandas型をPython intに変換"""
        if pd.isna(value):
            return None
        return int(value)

    def _save_single_ticker(self, data: pd.DataFrame, code: str) -> int:
        """単一銘柄の株価データを保存する"""
        saved_count = 0

        for idx, row in data.iterrows():
            trade_date = idx.date() if hasattr(idx, "date") else idx

            # NaNチェック
            if pd.isna(row.get("Close")):
                continue

            stmt = insert(StockPrice).values(
                code=code,
                trade_date=trade_date,
                open=self._to_float(row.get("Open")),
                high=self._to_float(row.get("High")),
                low=self._to_float(row.get("Low")),
                close=self._to_float(row.get("Close")),
                volume=self._to_int(row.get("Volume")),
                adjusted_close=self._to_float(row.get("Adj Close")),
            )
            stmt = stmt.on_conflict_do_update(
                constraint="uq_stock_price_code_date",
                set_={
                    "open": stmt.excluded.open,
                    "high": stmt.excluded.high,
                    "low": stmt.excluded.low,
                    "close": stmt.excluded.close,
                    "volume": stmt.excluded.volume,
                    "adjusted_close": stmt.excluded.adjusted_close,
                },
            )
            self.db.execute(stmt)
            saved_count += 1

        self.db.commit()
        return saved_count
