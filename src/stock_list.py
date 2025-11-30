"""日本株の銘柄リストを取得するモジュール"""

import io
import logging
from dataclasses import dataclass
from pathlib import Path

import pandas as pd
import requests

logger = logging.getLogger(__name__)

# JPX（日本取引所グループ）の上場銘柄一覧URL
JPX_STOCK_LIST_URL = "https://www.jpx.co.jp/markets/statistics-equities/misc/tvdivq0000001vg2-att/data_j.xls"

# キャッシュファイルパス
CACHE_DIR = Path("/app/data")
CACHE_FILE = CACHE_DIR / "stock_list.csv"


@dataclass
class StockInfo:
    code: str
    name: str
    market: str = "TSE"
    sector: str = ""


def fetch_jpx_stock_list() -> list[StockInfo]:
    """JPXから上場銘柄一覧を取得する"""
    logger.info("Fetching stock list from JPX...")

    try:
        response = requests.get(JPX_STOCK_LIST_URL, timeout=30)
        response.raise_for_status()

        # Excelファイルを読み込み
        df = pd.read_excel(io.BytesIO(response.content))

        stocks = []
        for _, row in df.iterrows():
            code = str(row.get("コード", "")).strip()
            name = str(row.get("銘柄名", "")).strip()
            market = str(row.get("市場・商品区分", "")).strip()
            sector = str(row.get("33業種区分", "")).strip()

            # 有効な銘柄コードのみ（4桁の数字）
            if code and code.isdigit() and len(code) == 4:
                stocks.append(
                    StockInfo(
                        code=code,
                        name=name,
                        market=market,
                        sector=sector,
                    )
                )

        logger.info(f"Fetched {len(stocks)} stocks from JPX")

        # キャッシュに保存
        _save_cache(stocks)

        return stocks

    except Exception as e:
        logger.error(f"Failed to fetch stock list from JPX: {e}")
        # キャッシュから読み込み
        cached = _load_cache()
        if cached:
            logger.info(f"Using cached stock list ({len(cached)} stocks)")
            return cached
        raise


def _save_cache(stocks: list[StockInfo]) -> None:
    """銘柄リストをキャッシュに保存"""
    try:
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        df = pd.DataFrame([vars(s) for s in stocks])
        df.to_csv(CACHE_FILE, index=False)
        logger.info(f"Saved stock list cache to {CACHE_FILE}")
    except Exception as e:
        logger.warning(f"Failed to save cache: {e}")


def _load_cache() -> list[StockInfo] | None:
    """キャッシュから銘柄リストを読み込み"""
    try:
        if CACHE_FILE.exists():
            df = pd.read_csv(CACHE_FILE, dtype=str)
            stocks = [
                StockInfo(
                    code=row["code"],
                    name=row["name"],
                    market=row.get("market", "TSE"),
                    sector=row.get("sector", ""),
                )
                for _, row in df.iterrows()
            ]
            return stocks
    except Exception as e:
        logger.warning(f"Failed to load cache: {e}")
    return None


def get_stock_list(use_cache: bool = True) -> list[StockInfo]:
    """
    日本株の銘柄リストを取得する

    Args:
        use_cache: キャッシュがあれば使用する（デフォルト: True）

    Returns:
        銘柄リスト
    """
    if use_cache:
        cached = _load_cache()
        if cached:
            logger.info(f"Using cached stock list ({len(cached)} stocks)")
            return cached

    return fetch_jpx_stock_list()


def get_yahoo_ticker(code: str) -> str:
    """銘柄コードをYahoo Finance用のティッカーシンボルに変換"""
    return f"{code}.T"
