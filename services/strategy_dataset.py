import warnings
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
import yfinance as yf
import datetime as dt
import matplotlib.pyplot as plt

from typing import List, Optional, Dict


class FinancialData:
     # initialize function
     def __init__(self, symbol: str, end_day: str, days: int, capital: int) -> None:
          self.symbol = symbol
          self.start = end_day - pd.Timedelta(days=days)
          self.end = end_day
          self.capital = capital
          self.load_data()
          self.add_daily_returns()

     def load_data(self) -> None:
          try:
               self.data = yf.download(tickers=self.symbol, start=self.start, end=self.end)
          except:
               raise ValueError("The stock name you input is not exist!")

     # preparing data - adding daily returns and buy/hold returns column
     def add_daily_returns(self) -> None:
          self.data['daily_returns'] = np.log(self.data['Adj Close'] / self.data['Adj Close'].shift(1))
          self.data['bnh_returns'] = self.data['daily_returns'].cumsum()
