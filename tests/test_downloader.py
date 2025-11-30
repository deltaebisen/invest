"""ダウンローダーのテスト"""

import pytest
from unittest.mock import MagicMock, patch
import pandas as pd
from datetime import datetime

from src.stock_list import get_stock_list, get_yahoo_ticker, StockInfo


def test_get_stock_list():
    """銘柄リストが取得できることを確認"""
    stocks = get_stock_list()
    assert len(stocks) > 0
    assert all(isinstance(s, StockInfo) for s in stocks)


def test_get_yahoo_ticker():
    """Yahoo Financeティッカー変換のテスト"""
    assert get_yahoo_ticker("7203") == "7203.T"
    assert get_yahoo_ticker("9984") == "9984.T"


def test_stock_info():
    """StockInfoデータクラスのテスト"""
    stock = StockInfo(code="7203", name="トヨタ自動車")
    assert stock.code == "7203"
    assert stock.name == "トヨタ自動車"
    assert stock.market == "TSE"
