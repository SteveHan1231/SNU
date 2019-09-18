# -*- coding: utf-8 -*-
"""
implied volatility with futures price under any circumstances

@author: Minkyu Han
"""
import numpy as np
import pandas as pd
import time
import datetime as dt
from scipy.special import erf
import bond_price_interpolation
import matplotlib.pyplot as plt
#import pandas_datareader as web


ticker = input("Enter ticker : ")
print("Computing...")
option_data = ticker + '_option.xlsx'
futures_data = ticker + '_futures.xlsx'
start = time.time()


option_prices = pd.read_excel(option_data,sheet_name='price')
option_prices = option_prices.drop(range(3))
option_prices = option_prices.drop(4)

temp = option_prices.columns
option_list = []
for t in temp:
    if type(option_prices[t][3])==float:
        option_prices = option_prices.drop(t,axis=1)
    elif ticker in option_prices[t][3]:
        option_list.append(option_prices[t][3][:-4])

option_prices.index = option_prices['Start']
option_prices = option_prices.drop('Start',axis=1)
option_prices.columns = option_list
option_prices = option_prices.drop('Code')

days = (option_prices.index).tolist()
n = len(days)

expiry = pd.read_excel(option_data,sheet_name='expiry date')
expiry = expiry.drop(0)
expiry.index = expiry['Date']
expiry = expiry.drop('Date',axis=1)
expiry = expiry.loc[option_list]
expiry = expiry.drop(expiry.columns[1],axis=1)
temp = np.array(expiry).tolist()
m = len(temp)
temp = np.array(temp*n)
temp = temp.reshape((n,m))
expiry = pd.DataFrame(temp, index = days, columns = option_list)
today = np.array(days*m).reshape((m,n)).transpose()
ttt = temp-today
for i in range(ttt.shape[0]):
    for j in range(ttt.shape[1]):
        ttt[i,j] = ttt[i,j].days
ttt = np.array(ttt.tolist())

T = pd.DataFrame(ttt/365,index=days,columns=option_list)

strike = pd.read_excel(option_data,sheet_name='strike price')
strike = strike.drop(0)
strike.index = strike['Date']
strike = strike.drop('Date',axis=1)
strike = strike.loc[option_list]
strike = strike.drop(strike.columns[1],axis=1)
temp = np.array(strike).tolist()
m = len(temp)
temp = np.array(temp*n)
temp = temp.reshape((n,m))
strike = pd.DataFrame(temp, index = days, columns = option_list)


option_type = option_list.copy()
for j in range(len(option_type)):
    option_type[j] = option_type[j][-1]

option_type = np.array(option_type*n).reshape((n,len(option_type)))
option_type = pd.DataFrame(option_type, index = days, columns=option_list)



futures = pd.read_excel(futures_data, sheet_name = 'futures price')
delivery = pd.read_excel(futures_data, sheet_name = 'futures settlement date')

futures.columns = range(len(futures.columns))
futures = futures.drop(range(3))
for i in range(1,len(futures.columns)):
    if type(futures[i][3])==float:
        futures = futures.drop(i,axis=1)
        
#futures.columns = futures.loc[3]
futures_list = []
for j in range(1,len(futures.columns)):
    futures_list.append(futures[futures.columns[j]][3][:-4])

futures = futures.drop([3,4])
futures.index = futures[futures.columns[0]]
futures = futures.drop(0,axis=1)
futures.columns = futures_list


delivery = delivery.transpose()
delivery.columns = delivery.iloc[1]
delivery = delivery.drop(delivery.index[1:3])
delivery = delivery.drop(delivery.columns[0],axis=1)


B = T.copy()
bond_price_interp = bond_price_interpolation.bond_price_interp
for j in range(len(bond_price_interp)):
    wh = B.iloc[j]>=0
    B.iloc[j][wh] = bond_price_interp[j](B.iloc[j][wh])


#data = web.data.DataReader(ticker, 'yahoo', dt.datetime(2018,12,31), dt.datetime(2019,3,31))['Adj Close']


F = pd.DataFrame(np.ones((len(option_prices.index),len(option_prices.columns))),index = option_prices.index, columns = option_prices.columns)
for i in delivery.columns:
    if delivery[i].iloc[0] not in futures.columns:
        delivery = delivery.drop(i,axis=1)
        
#temp = []
for j in F.columns:
    s = np.abs(delivery.columns-expiry[j].iloc[0]).min()
#    temp.append(s)
#    print(s)
    if s==dt.timedelta(0):
#        temp+=1
#        print(temp)
        F[j] = futures[delivery[delivery.columns[np.where(np.abs(delivery.columns-expiry[j].iloc[0])==s)]].iloc[0]]
    else:
        Tb = delivery.columns[delivery.columns<expiry[j].iloc[0]].max()
        Ta = delivery.columns[delivery.columns>expiry[j].iloc[0]].min()
        for k in F.index:
            fb = futures[delivery[Tb][0]][k]
            fa = futures[delivery[Ta][0]][k]
            if fb=='na' or fa=='na':
                F[j][k] = 'na'
            else:
                F[j][k] = fb + (fa-fb)*((expiry[j].iloc[0]-Tb)/(Ta-Tb))
#            print(F[j][k])
        
print('\a')
F = F.replace('na',-1)
F = pd.DataFrame(np.float32(F), index=F.index, columns=F.columns)
F = F.replace(-1,'na')
strike = pd.DataFrame(np.float32(strike), index=strike.index, columns=strike.columns)



del(wh,delivery,expiry,futures,futures_list,i,j,m,n,option_list,temp,today,ttt,futures_data,option_data)

x = np.linspace(0,3,1000)
bond_fig, bond_ax = plt.subplots()
for w in bond_price_interp:
    bond_ax.plot(x, w(x))
plt.xlabel('Time to maturity')
plt.ylabel('Bond price')
if bond_price_interpolation.s=='cs':
    s = 'cubic spline with 0 derivatives at the ends'
elif bond_price_interpolation.s=='l':
    s = 'linear interpolation'
plt.title('Bond price by ' + s)
plt.show()
plt.grid()
bond_fig.savefig('Bond Price by '+s)
#plt.close(bond_fig)
del(bond_fig,bond_ax,w,s)
# Now, the data is set

def Pricing(opt_type, B, F, K, T, v):
    d1 = np.log(F/K)/(v*np.sqrt(T))+v*np.sqrt(T)/2
    d2 = d1 - v*np.sqrt(T)
    c = B*(F*(erf(d1/np.sqrt(2))/2+0.5) - K*(erf(d2/np.sqrt(2))/2+0.5))
    if opt_type=='C':
        return c
    elif opt_type=='P':
        return c + B*(K-F)

def volatility(opt_type, B, F, K, T, p):
    v = 1e-10
    if Pricing(opt_type,B,F,K,T,v)>p:
        return 0
    else:
        while Pricing(opt_type,B,F,K,T,v)<p:
            v*=10
        b = v
        a = b/10
        while b-a>1e-10:
            if Pricing(opt_type,B,F,K,T,(a+b)/2)<p:
                a = (a+b)/2
            else:
                b = (a+b)/2
        return (a+b)/2

imp_vol = pd.DataFrame(np.ones_like(option_prices), index = option_prices.index, columns = option_prices.columns)*'na'

for d in days:
    target = (option_prices.loc[d]!='na')&(F.loc[d]!='na')
    p = option_prices.loc[d][target]
    p = pd.Series(np.float32(p),index=p.index)
    f = F.loc[d][target]
    f = pd.Series(np.float32(f),index=f.index)
    b = B.loc[d][target]
    b = pd.Series(np.float32(b),index=b.index)
    k = strike.loc[d][target]
    t = T.loc[d][target]
    t = pd.Series(np.float32(t),index=t.index)
    o = option_type.loc[d][target]
    temp = []
    for j in f.index:
        temp.append(volatility(o[j],b[j],f[j],k[j],t[j],p[j]))
    imp_vol.loc[d][f.index] = temp
    del(j,p,f,b,k,t,o,temp,target)
#    print('Computation time is %.2fsec'%(time.time()-start))
#    print('\a')


imp_vol.to_excel('implied volatility of '+ticker+' with futures.xlsx')








computation = time.time()-start
print('\aThe total computation time is %d hours %d minutes and %.2f seconds'%(int(computation//3600),int((computation%3600)//60),computation%60))