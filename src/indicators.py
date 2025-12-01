"""テクニカル指標を計算するモジュール"""

import pandas as pd


def calculate_ma(series: pd.Series, period: int) -> pd.Series:
    """移動平均を計算"""
    return series.rolling(window=period, min_periods=period).mean()


def calculate_rsi(series: pd.Series, period: int = 9) -> pd.Series:
    """RSIを計算"""
    delta = series.diff()
    gain = delta.where(delta > 0, 0.0)
    loss = (-delta).where(delta < 0, 0.0)

    avg_gain = gain.rolling(window=period, min_periods=period).mean()
    avg_loss = loss.rolling(window=period, min_periods=period).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi


def calculate_bollinger_bands(
    series: pd.Series, period: int = 20, num_std: float = 2.0
) -> tuple[pd.Series, pd.Series, pd.Series]:
    """ボリンジャーバンドを計算

    Returns:
        (upper, middle, lower)
    """
    middle = series.rolling(window=period, min_periods=period).mean()
    std = series.rolling(window=period, min_periods=period).std()
    upper = middle + (std * num_std)
    lower = middle - (std * num_std)
    return upper, middle, lower


def calculate_all_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """DataFrameに全てのテクニカル指標を追加

    Args:
        df: 'close'カラムを含むDataFrame

    Returns:
        テクニカル指標が追加されたDataFrame
    """
    close = df["close"]

    df["ma5"] = calculate_ma(close, 5)
    df["ma20"] = calculate_ma(close, 20)
    df["rsi9"] = calculate_rsi(close, 9)

    bb_upper, bb_middle, bb_lower = calculate_bollinger_bands(close, 20, 2.0)
    df["bb_upper"] = bb_upper
    df["bb_middle"] = bb_middle
    df["bb_lower"] = bb_lower

    return df
