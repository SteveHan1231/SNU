# -*- coding: utf-8 -*-
"""
realized roughness
"""
import numpy as np
import pandas as pd
from datetime import datetime as dt
from datetime import timedelta as td

ticker = input("Enter ticker : ")

prices = pd.read_csv(ticker+'_6M_2019_6_1MIN.csv')
prices.index = prices[prices.columns[0]]
prices = prices.drop(prices.columns[0], axis=1)




index = []
for t in prices.index:
    index.append(dt.strptime(t,'%Y.%m.%d %H:%M:%S'))
prices.index = index
price = prices[['close']]
index2 = np.array(index)

days = []
for t in index:
    if dt(t.year,t.month,t.day) not in days:
        days.append(dt(t.year,t.month,t.day))

RV = []

for t in days:
    times = index2[index2<t+td(days=1)]
#    print(times)
#    print("="*30)
    p = price.loc[times]
    iv = (np.log(p).diff().drop(p.index[0])**2).sum()[0]
    RV.append(iv)
    index2 = index2[times.size:]

vol = np.log(RV)
L = []
Z = []
N = len(RV)
for l in range(1,N):
    L.append(l)
    temp = vol[::l]
    Z.append((np.diff(temp)**2).sum()/(N-l))

L = np.log(L)
Z = np.log(Z)
b = ((L*Z).sum()-L.sum()*Z.sum()/len(L))/((L**2).sum()-(L.sum())**2/len(L))
H = b/2
#dt.strptime(prices.index[0], '%Y.%m.%d %H:%M:%S')