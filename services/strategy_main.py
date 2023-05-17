# import warnings
# warnings.filterwarnings("ignore")

# import numpy as np
# import pandas as pd
# import yfinance as yf
# import datetime as dt
# import matplotlib.pyplot as plt
# # import pyfolio as pf

# from strategy_models import BollingerModel, KdModel, RsiModel

# MAX_TRY = 3

# def user_input(max_try):
#     for _ in range(max_try):

#         stock = input("Please enter the stock name: ")

#         try:
#             days = int(input("Please enter how many days you want to test from now: "))
#             end_day = dt.datetime.today()
#         except:
#             print("The days you input is not valid !")
#             continue

#         try:
#             capital = int(input("Please enter the capital you want to invest: "))
#         except:
#             print("The capital you input is not valid !")
#             continue

#         try:
#             strategy = int(input("Please choose the strategy you want to use(enter one of the numbers below):\n1.Boll 2.KD 3.RSI\n"))
#         except:
#             print("The number you input is not valid !")
#             continue

#         if strategy < 1 or strategy > 3:
#             print('The strategy number must be in the range from 1 to 3 !')
#             continue

#         break
        
#     return stock, days, end_day, capital, strategy
            

# def write_xlsx(self, file_name):
#     with pd.ExcelWriter(file_name) as writer:
#         self.data.to_excel(writer)


# if __name__ == "__main__":
#     stock, days, end_day, capital, strategy = user_input(MAX_TRY)
#     # users choose Bollinger
#     if strategy == 1:
#         boll = BollingerModel(symbol=stock, end_day=end_day, days=days, capital=capital)
#         try:
#             start = int(input("Please input the minimum MA you want to use: "))
#             end = int(input("Please input the maximum MA you want to use: "))
#         except:
#             raise ValueError("The MA you input is not valid!")
#         if start > end:
#             raise ValueError("The minimum MA should not be larger than the maximum MA !")

#         best_window, best_dr, best_sr = boll.optimizer(start, end)
#         print(best_window, best_dr, best_sr)
#         boll.plot_equity_curve(best_window)
    
#     # users choose KD
#     elif strategy == 2:
#         try:
#             start = int(input("Please input the minimum number of days in the past you want to use: "))
#             end = int(input("Please input the maximum number of days in the past you want to use: "))
#         except:
#             raise ValueError("The the number of days you input is not valid!")
#         if start > end:
#             raise ValueError("The minimum number of days in the past should not be larger than the maximum number of days in the past !")
        
#         k_value = 50
#         kd = KdModel(symbol=stock, end_day=end_day, days=days, capital=capital, k=k_value)
#         best_window, best_dr, best_sr = kd.optimizer(start, end)
#         print(best_window, best_dr, best_sr)
#         kd.plot_equity_curve(best_window)
    
#     # users choose RSI
#     elif strategy == 3:
#         try:
#             start_short = int(input("Please input the minimum slow line you want to use: "))
#             end_short = int(input("Please input the maximum slow line you want to use: "))
#             start_long = int(input("Please input the minimum long line you want to use: "))
#             end_long = int(input("Please input the maximum long line you want to use: "))
#         except:
#             raise ValueError("The line(number of days) you input is not valid!")
#         if start_short > end_short:
#             raise ValueError("The minimum slow line should not be larger than the maximum slow line!")
#         elif start_long > end_long:
#             raise ValueError("The minimum long line should not be larger than the maximum long line!")
#         elif start_long <= end_short:
#             raise ValueError("The minimum long line should not be smaller than or equal to the maximum slow line!")

#         rsi = RsiModel(symbol=stock, end_day=end_day, days=days, capital=capital)
#         max_short, max_long, max_dr, max_sr = \
#             rsi.optimizer(start_short, end_short, start_long, end_long)
#         print(max_short, max_long, max_dr, max_sr)
#         rsi.plot_equity_curve(max_short, max_long)
