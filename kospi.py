# -*- coding: utf-8 -*-
"""
Created on Sun Aug  9 03:24:31 2020

@author: Minkyu Han
"""

import numpy as np
import pandas_datareader as pdd
from datetime import datetime as dt
from dateutil.relativedelta import relativedelta as rtd
import matplotlib.pyplot as plt
import time
f = open("kospi200_ticker.txt", "r")
ticker = [x.strip('\n') for x in f]
today = dt.today()
begin = today-rtd(years=1)

start = time.time()
data = pdd.DataReader(ticker, 'yahoo', begin, today)['Adj Close']

first_price = data.iloc[0]
first_price = first_price.fillna(-1)
failed_ticker = first_price.index[first_price==-1].tolist()

good_ticker = list(set(ticker)-set(failed_ticker))
prices = data[good_ticker]
values = prices/prices.iloc[0]



print("Computation time is %.2fsec"%(time.time()-start))