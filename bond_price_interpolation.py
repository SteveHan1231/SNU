# -*- coding: utf-8 -*-
"""
bond price interpolation

@author: Minkyu Han
"""
import numpy as np
import pandas as pd
from datetime import datetime as dt
#import matplotlib.pyplot as plt
from scipy.interpolate import CubicSpline, interp1d

use = input("what to use? (CPN/PRCL) : ")

bond = pd.read_excel('bond.xlsx', sheet_name='bond price')
bond = bond.drop([0,1,3,4])
bond.columns = range(len(bond.columns))
for j in bond.columns:
    if (bond[j].iloc[0]!='Name') and (use not in bond[j].iloc[0]):
        bond = bond.drop(j,axis=1)
del(j)
bond.index = bond[bond.columns[0]]
bond = bond.drop(bond.columns[0],axis=1)



def remoch(s):
    l = '/0123456789'
    for x in s:
        if x not in l:
            s = s.replace(x,'')
    return s

#def is_decreasing(x):
#    temp = 0
#    while x[temp+1]<=x[temp]:
#        temp+=1
#    if temp==len(x)-1:
#        return True
#    else:
#        print(temp)
#        return False


bond_list = []
for s in bond.iloc[0]:
    bond_list.append(dt.strptime(remoch(s)[-8:], '%d/%m/%y'))
del(s)

bond.columns = bond.iloc[0].copy()
bond.index=['maturity']+bond.index.tolist()[1:]
bond.loc['maturity'] = bond_list
bond = bond.sort_values(by='maturity', axis=1)
bond.columns = bond.loc['maturity']
temp = []
for j in bond.index[1:]:
    for k in range(len(bond.columns)-1):
        if bond.loc[j][k]!='na' and bond.loc[j][k+1]!='na':
            if bond.loc[j][k]<bond.loc[j][k+1]:
                temp.append(bond.iloc[0][k+1])
temp = list(set(temp))
bond = bond.drop(temp,axis=1)
bond.columns = range(len(bond.columns))
bond_price_interp = []
e = np.linspace(0,2,1000)
s = input("Bond price interpolation type? (cubic:cs/linear:l) : ")
for j in bond.index[1:]:
    l = (bond.loc[j][bond.loc[j]!='na']).index
    t = np.array(((bond.iloc[0][l]-j).values/(1e9)/3600/24).tolist())/365
    x = list(set(t))
    x.sort()
    p = np.array(bond[l].loc[j])
    y=[]
    for k in x:
        y.append(p[np.where(t==k)[0]].mean())
    del(k)
    #plt.plot(x,y)
    x = np.flip(x)
    x = np.append(x,0)
    x = np.flip(x)
    y = np.flip(y)/100
    y = np.append(y,1)
    y = np.flip(y)
#    if is_decreasing(y)==False:
#        temp_fig, temp_ax = plt.subplots()
#        temp_ax.plot(x,y)
#        temp_ax.set_xlabel('time to maturity')
#        temp_ax.set_ylabel('bond price')
#        temp_ax.title.set_text(dt.strftime(j,'%y/%m/%d'))
#        plt.show()
#        del(temp_fig,temp_ax)
    if s=='cs':
        cs = CubicSpline(x,y, bc_type='clamped')
    elif s=='l':
        cs = interp1d(x,y)
    bond_price_interp.append(cs)
    
    #plt.plot(e, cs(e))
    del(l,t,x,p,y,cs)

#del(j,e,bond,bond_list)
    
























