import warnings
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
import yfinance as yf
import datetime as dt
import matplotlib.pyplot as plt
import pyfolio as pf
# import talib

from services.strategy_dataset import FinancialData


def prepare_positions_and_calculate_returns(self, window=None, short=None, long=None) -> float:
        # prepare indicators
        self.prepare_indicators(window, short, long)

        # prepare signal
        self.prepare_signals(window, short, long)

        # prepare positions and calculate equity 
        holdings_strategy, holdings_bnh = 0, self.capital / self.data["Adj Close"].iloc[0]
        capital_strategy = self.capital
        positions, daily_equity, strategy_equity = [], [], []
        for day in range(len(self.data)):
            # calculate positions
            if self.data["signal"].iloc[day] == 1:
                if not holdings_strategy:
                    holdings_strategy = capital_strategy / self.data["Adj Close"].iloc[day]
                    capital_strategy = 0
            elif self.data["signal"].iloc[day] == -1:
                if holdings_strategy:
                    capital_strategy += holdings_strategy * self.data["Adj Close"].iloc[day]
                    holdings_strategy = 0
            positions.append(holdings_strategy)

            # calculate equity
            strategy_equity.append(capital_strategy + holdings_strategy * self.data["Adj Close"].iloc[day])
            daily_equity.append(holdings_bnh * self.data["Adj Close"].iloc[day])
        self.data["position"] = positions
        self.data["strategy_equity"] = strategy_equity
        self.data["daily_equity"] = daily_equity

        # calculate returns
        strategy_returns = (capital_strategy + self.data["position"].iloc[-1] * self.data["Adj Close"].iloc[-1] - \
            self.capital) / self.capital
        daily_returns = (self.data["daily_equity"].iloc[-1] - self.capital) / self.capital

        return daily_returns, strategy_returns


class BollingerModel(FinancialData):
    def __init__(self, symbol: str, end_day: str, days: int, capital: int) -> None:
        super(BollingerModel, self).__init__(symbol, end_day, days, capital)

    # note: 0th ~ "window - 1"th data will be NaN
    def prepare_indicators(self, window: int, short: None, long: None) -> None:
        self.data['moving_avg'] = \
            self.data['Adj Close'].rolling(window=window).mean()
        self.data['moving_std'] = \
            self.data['Adj Close'].rolling(window=window).std()
    
        self.data['upper_band'] = \
            self.data['moving_avg'] + 2 * self.data['moving_std']
        self.data['lower_band'] = \
            self.data['moving_avg'] - 2 * self.data['moving_std']

    # add signal
    # buy: 1
    # sell: -1
    def prepare_signals(self, window: int, short: None, long: None) -> None:
        buy_condition = []
        for day in range(len(self.data)):
            if day <= window:
                buy_condition.append(0)
            # buy
            elif self.data['Adj Close'].iloc[day-1] < self.data['lower_band'].iloc[day-1] and \
                self.data['Adj Close'].iloc[day] >= self.data['lower_band'].iloc[day]:
                    buy_condition.append(1)
            # sell
            elif self.data['Adj Close'].iloc[day-1] > self.data['upper_band'].iloc[day-1] and \
                    self.data['Adj Close'].iloc[day] <= self.data['upper_band'].iloc[day]:
                        buy_condition.append(-1)
            # do nothing
            else:
                buy_condition.append(0)
        self.data['signal'] = buy_condition

    def boll_calculate_returns(self, window: int) -> float:
        return prepare_positions_and_calculate_returns(self=self, window=window)
    
    def optimizer(self, start_window: int, end_window: int):
        max_dr, max_sr, max_window = -1, -1, -1
        for window in range(start_window, end_window+1):
            curr_dr, curr_sr = self.boll_calculate_returns(window)
            if curr_sr > max_sr:
                max_sr = curr_sr
                max_dr = curr_dr
                max_window = window
        return max_window, max_dr, max_sr

    def plot_equity_curve(self, max_window):
        tmp1, tmp2 = self.boll_calculate_returns(max_window)
        self.data[["daily_equity", "strategy_equity"]].plot()
        plt.show()


class KdModel(FinancialData):
    def __init__(self, symbol: str, end_day: str, days: int, capital: int, k: int) -> None:

        super(KdModel, self).__init__(symbol, end_day, days, capital)
        self.k = k  # initialize to 50
    
    def prepare_indicators(self, window: int, short: None, long: None) -> None:
        self.data["past_n_high"] = self.data['Adj Close'].rolling(window=window).max()
        self.data["past_n_low"] = self.data['Adj Close'].rolling(window=window).min()
        self.data["rsv"] = 100 * ((self.data['Adj Close'] - self.data["past_n_low"]) / \
            (self.data["past_n_high"] - self.data["past_n_low"]))
        
        values_k, values_d = [], []
        for day in range(len(self.data)):
            # initialize to 50
            if day < window - 1:
                values_k.append(self.k)
                values_d.append(self.k)
            else:
                values_k.append(2/3 * values_k[day-1] + 1/3 * self.data["rsv"].iloc[day])
                values_d.append(2/3 * values_d[day-1] + 1/3 * values_k[day])
        self.data["k_value"] = values_k
        self.data["d_value"] = values_d

    def prepare_signals(self, window: int, short: None, long: None) -> None:
        signal = []
        for day in range(len(self.data)):
            # note: the first valid signal must be the "window"th data
            if day <= window - 1:
                signal.append(0)
            # buy
            elif self.data["k_value"].iloc[day-1] < self.data["d_value"].iloc[day-1] and \
                self.data["k_value"].iloc[day] >= self.data["d_value"].iloc[day]:
                    signal.append(1)
            # sell
            elif self.data["k_value"].iloc[day-1] > self.data["d_value"].iloc[day-1] and \
                    self.data["k_value"].iloc[day] <= self.data["d_value"].iloc[day]:
                        signal.append(-1)
            # do nothing
            else:
                signal.append(0)
        self.data["signal"] = signal

    def kd_calculate_returns(self, window: int) -> float:
        return prepare_positions_and_calculate_returns(self=self, window=window)

    def optimizer(self, start_window: int, end_window: int):
        max_dr, max_sr, max_window = -1, -1, -1
        for window in range(start_window, end_window+1):
            curr_dr, curr_sr = self.kd_calculate_returns(window)
            if curr_sr > max_sr:
                max_sr = curr_sr
                max_dr = curr_dr
                max_window = window
        return max_window, max_dr, max_sr

    def plot_equity_curve(self, max_window):
        tmp1, tmp2 = self.kd_calculate_returns(max_window)
        self.data[["daily_equity", "strategy_equity"]].plot()
        plt.show()


class RsiModel(FinancialData):
    def __init__(self, symbol: str, end_day: str, days: int, capital: int) -> None:
        super(RsiModel, self).__init__(symbol, end_day, days, capital)

    def prepare_indicators(self, window: None, short: int, long: int) -> None:
        def sum_positive(arr):
            return sum(i for i in arr if i > 0)
        def sum_total(arr):
            return sum(abs(i) for i in arr)
        
        self.data["diff"] =  self.data['Adj Close'] - self.data['Adj Close'].shift(1)
        
        # calculate daily fluctuation
        fluctuates = []
        for day in range(len(self.data)):
            if day == 0:
                fluctuates.append(np.nan)
            else:
                fluctuates.append(self.data["diff"].iloc[day] / self.data["Adj Close"].iloc[day-1])
        self.data["daily_fluctuation"] = fluctuates

        # calculat short and long RSI
        self.data["short_rsi"] = 100 * (self.data["daily_fluctuation"].rolling(short).apply(sum_positive) / \
            self.data["daily_fluctuation"].rolling(short).apply(sum_total))
        self.data["long_rsi"] = 100 * (self.data["daily_fluctuation"].rolling(long).apply(sum_positive) / \
            self.data["daily_fluctuation"].rolling(long).apply(sum_total))

    def prepare_signals(self, window: None, short: None, long: int) -> None:
        signal = []
        for day in range(len(self.data)):
            if day <= long:
                signal.append(0)
            elif self.data["short_rsi"].iloc[day-1] < self.data["long_rsi"].iloc[day-1] and \
                self.data["short_rsi"].iloc[day] >= self.data["long_rsi"].iloc[day]:
                    signal.append(1)
            elif self.data["short_rsi"].iloc[day-1] > self.data["long_rsi"].iloc[day-1] and \
                self.data["short_rsi"].iloc[day] <= self.data["long_rsi"].iloc[day]:
                    signal.append(-1)
            else:
                signal.append(0)
        self.data["signal"] = signal

    def rsi_calculate_returns(self, short: int, long: int) -> float:
        return prepare_positions_and_calculate_returns(self=self, short=short, long=long)
    
    def optimizer(self, short_start: int, short_end: int, long_start: int, long_end: int):
        max_dr, max_sr, max_short, max_long = -1, -1, -1, -1
        for short in range(short_start, short_end+1):
            for long in range(long_start, long_end+1):
                curr_dr, curr_sr = self.rsi_calculate_returns(short=short, long=long)
                if curr_sr > max_sr:
                    max_sr = curr_sr
                    max_dr = curr_dr
                    max_short = short
                    max_long = long
        return max_short, max_long, max_dr, max_sr

    def plot_equity_curve(self, max_short: int, max_long: int):
        tmp1, tmp2 = self.rsi_calculate_returns(short=max_short, long=max_long)
        self.data[["daily_equity", "strategy_equity"]].plot()
        plt.show()


class SMAModel(FinancialData):
    def __init__(self, symbol: str, end_day: str, days: int, capital: int) -> None:
        super(SMAModel, self).__init__(symbol, end_day, days, capital)

    def prepare_indicators(self, window: None, short: int, long: int) -> None:
        self.data['Long SMA'] = talib.SMA(self.data['Adj Close'], timeperiod=long)
        self.data['Short SMA'] = talib.SMA(self.data['Adj Close'], timeperiod=short)

    def prepare_signals(self, window: None, short: None, long: int) -> None:
        signal = []
        for day in range(len(self.data)):
            if day <= long:
                signal.append(0)
            elif self.data['Adj Close'].iloc[day-1] > self.data['Long SMA'].iloc[day-1]:
                    signal.append(1)
            elif self.data['Adj Close'].iloc[day-1] < self.data['Short SMA'].iloc[day-1]:
                    signal.append(-1)
            else:
                signal.append(0)
        self.data['signal'] = signal

    def SMA_calculate_returns(self, short: int, long: int) -> float:
        return prepare_positions_and_calculate_returns(self=self, short=short, long=long)
    
    def optimizer(self, short_start: int, short_end: int, long_start: int, long_end: int):
        max_dr, max_sr, max_short, max_long = -1, -1, -1, -1
        for short in range(short_start, short_end+1):
            for long in range(long_start, long_end+1):
                curr_dr, curr_sr = self.SMA_calculate_returns(short=short, long=long)
                if curr_sr > max_sr:
                    max_sr = curr_sr
                    max_dr = curr_dr
                    max_short = short
                    max_long = long
        return max_short, max_long, max_dr, max_sr

    def plot_equity_curve(self, max_short: int, max_long: int):
        tmp1, tmp2 = self.SMA_calculate_returns(short=max_short, long=max_long)
        self.data[["daily_equity", "strategy_equity"]].plot()
        plt.show()


class MACDModel(FinancialData):
    def __init__(self, symbol: str, end_day: str, days: int, capital: int) -> None:
        super(MACDModel, self).__init__(symbol, end_day, days, capital)

    def prepare_indicators(self, window: None, short: int, long: int) -> None:
        self.data['Short EMA'] = talib.EMA(self.data['Adj Close'], short)
        self.data['Long EMA'] = talib.EMA(self.data['Adj Close'], long)
        self.data['DIFF'], self.data['DEM'], self.data['OSC'] = talib.MACD(self.data['Adj Close'], short, long, 9)

    def prepare_signals(self, window: None, short: int, long: int) -> None:
        signal = []
        for day in range(len(self.data)):
            if day <= long:
                signal.append(0)
            elif self.data['DIFF'].iloc[day-2] <= self.data['DEM'].iloc[day-2] and \
                    self.data['DIFF'].iloc[day-1] > self.data['DEM'].iloc[day-1]:
                    signal.append(1)
            elif self.data['DIFF'].iloc[day-2] >= self.data['DEM'].iloc[day-2] and \
                    self.data['DIFF'].iloc[day-1] < self.data['DEM'].iloc[day-1]:
                    signal.append(-1)
            else:
                signal.append(0)
        self.data['signal'] = signal

    def MACD_calculate_returns(self, short: int, long: int) -> float:
        return prepare_positions_and_calculate_returns(self=self, short=short, long=long)

    def optimizer(self, short_start: int, short_end: int, long_start: int, long_end: int):
        max_dr, max_sr, max_short, max_long = -1, -1, -1, -1
        for short in range(short_start, short_end+1):
            for long in range(long_start, long_end+1):
                curr_dr, curr_sr = self.MACD_calculate_returns(short=short, long=long)
                if curr_sr > max_sr:
                    max_sr = curr_sr
                    max_dr = curr_dr
                    max_short = short
                    max_long = long
        return max_short, max_long, max_dr, max_sr

    def plot_equity_curve(self, max_short: int, max_long: int):
        tmp1, tmp2 = self.MACD_calculate_returns(short=max_short, long=max_long)
        self.data[["daily_equity", "strategy_equity"]].plot()
        plt.show()
