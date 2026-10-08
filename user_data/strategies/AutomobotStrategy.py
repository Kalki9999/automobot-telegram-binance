from pandas import DataFrame

import talib.abstract as ta
from freqtrade.strategy import IStrategy


class AutomobotStrategy(IStrategy):
    """
    Automobot v3
    V2 entry logic with less-reactive exits.

    Research/backtesting/dry-run only.
    """

    INTERFACE_VERSION = 3

    timeframe = "5m"
    can_short = False

    minimal_roi = {
        "0": 0.015,
        "30": 0.008,
        "60": 0.0,
    }

    stoploss = -0.015

    trailing_stop = False

    process_only_new_candles = True
    startup_candle_count = 250

    def populate_indicators(
        self,
        dataframe: DataFrame,
        metadata: dict,
    ) -> DataFrame:

        dataframe["ema20"] = ta.EMA(dataframe, timeperiod=20)
        dataframe["ema50"] = ta.EMA(dataframe, timeperiod=50)
        dataframe["ema200"] = ta.EMA(dataframe, timeperiod=200)

        dataframe["rsi"] = ta.RSI(dataframe, timeperiod=14)
        dataframe["adx"] = ta.ADX(dataframe, timeperiod=14)
        dataframe["atr"] = ta.ATR(dataframe, timeperiod=14)

        dataframe["atr_pct"] = (
            dataframe["atr"] / dataframe["close"]
        )

        dataframe["volume_mean"] = (
            dataframe["volume"].rolling(20).mean()
        )

        return dataframe

    def populate_entry_trend(
        self,
        dataframe: DataFrame,
        metadata: dict,
    ) -> DataFrame:

        dataframe.loc[
            (
                (dataframe["close"] > dataframe["ema200"])
                & (dataframe["ema20"] > dataframe["ema50"])
                & (dataframe["adx"] > 20)
                & (dataframe["rsi"] > 52)
                & (dataframe["rsi"] < 68)
                & (dataframe["volume"] > dataframe["volume_mean"])
                & (dataframe["volume"] > 0)
                & (dataframe["atr_pct"] > 0.001)
            ),
            "enter_long",
        ] = 1

        return dataframe

    def populate_exit_trend(
        self,
        dataframe: DataFrame,
        metadata: dict,
    ) -> DataFrame:

        # Exit only when both trend and momentum have
        # materially deteriorated. This avoids exiting
        # immediately on a normal short-term pullback.
        dataframe.loc[
            (
                (dataframe["ema20"] < dataframe["ema50"])
                & (dataframe["rsi"] < 42)
            ),
            "exit_long",
        ] = 1

        return dataframe
