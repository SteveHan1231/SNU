# -*- coding: utf-8 -*-
"""
implied volatility surface

@author: Minkyu Han
"""
import numpy as np
import matplotlib.pyplot as plt
import time
import pandas as pd
from scipy.interpolate import CubicSpline
from datetime import datetime as dt
start = time.time()
import implied_vol
v = implied_vol.imp_vol
F = implied_vol.F
K = implied_vol.strike
T = implied_vol.T
O = implied_vol.option_type
days = implied_vol.days
h = 1e-10
#call_list = []
#put_list = []
roughness = []
model_consis = []
negative_H = []
above_bound_H = []
#fig, ax = plt.subplots()
for d in days:
    l = (v.loc[d]!='na') & (v.loc[d]!=0)
    o = O.loc[d][l]
    f = F.loc[d][l]
    k = K.loc[d][l]
    t = T.loc[d][l]
    ttt = list(set(t))
    ttt.sort()
    if 0 in ttt:
        ttt.remove(0)
    p = (f>k) & (o=='P')
    c = (f<=k) & (o=='C')
    skew = []
    tau = []
    for maturity in ttt:
        log_mc = np.log(np.float32(k[c][t[c]==maturity]/f[c][t[c]==maturity]))
        volc = v.loc[d][l][c][t[c]==maturity]
        log_mp = np.log(np.float32(k[p][t[p]==maturity]/f[p][t[p]==maturity]))
        volp = v.loc[d][l][p][t[p]==maturity]
        data = pd.DataFrame(np.array([log_mp.tolist()+log_mc.tolist(),volp.tolist()+volc.tolist()]), index = ['log_moneyness','implied volatility']).transpose()
        data = data.sort_values(by='log_moneyness')
        data.index = range(len(data.index))
        tau.append(maturity)
        cs = CubicSpline(data['log_moneyness'], data['implied volatility'])
        skew.append(abs((cs(h)-cs(0))/h))
#        temp_fig, temp_ax = plt.subplots()
#        temp_ax.scatter(log_mp.tolist()+log_mc.tolist(), volp.tolist()+volc.tolist())
#        plt.title('maturity = %.2f'%(maturity))
#        del(temp_fig,temp_ax)
        del(log_mc, volc, log_mp, volp, data, cs)
    #plt.show()
    x = np.log(tau)
    y = np.log(skew)
    H = 0.5+( (x*y).sum() - x.sum()*y.sum()/len(x) )/((x**2).sum() - (x.sum())**2/len(x))
    roughness.append(H)
    if H<=0:
        negative_H.append(d)
    if H>=1:
        above_bound_H.append(d)
    if (H>0)&(H<1):
        model_consis.append(d)
        fig, ax = plt.subplots(2,1,False)
        fig.set_size_inches(20,20)
        ax[0].scatter(np.array(tau),np.array(skew))
        ax[1].scatter(x,y,c='r')
        #ax[1,0].(x,y)
        ax[0].set_title(dt.strftime(d,'%y/%m/%d'))
        ax[0].set_xlabel('time to maturity')
        ax[0].set_ylabel('skewness')
        ax[1].set_xlabel('log of time to maturity')
        ax[1].set_ylabel('log of skewness')
        ax[0].grid()
        ax[1].grid()
        plt.show()
        name = implied_vol.ticker+' t vs skewness at '+dt.strftime(d,'%y-%m-%d')
        fig.savefig(name)
        plt.close(fig)
        del(fig,ax,name)
    #put_list.append(p)
    #call_list.append(c)
    del(l,o,f,k,t,ttt,skew,tau,p,c,x,y,H)
del(d)


roughness = pd.Series(roughness, index = days)
print('max = ',roughness.max(), 'min = ', roughness.min())
print(roughness[model_consis])

roughness.to_excel('implied roughness of '+implied_vol.ticker+'.xlsx')

computation = time.time()-start
print('\aThe total computation time is %d hours %d minutes and %.2f seconds'%(int(computation//3600),int((computation%3600)//60),computation%60))









