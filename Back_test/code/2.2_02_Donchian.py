# -*- coding: utf-8 -*-
"""
Created on Sun Aug 20 14:59:48 2023

@author: 52207
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

ChinaUnicom=pd.read_csv('ChinaUnicom.csv')
ChinaUnicom.index=ChinaUnicom.iloc[:,1]
ChinaUnicom.index=pd.to_datetime(ChinaUnicom.index, format='%Y-%m-%d')
ChinaUnicom=ChinaUnicom.iloc[:,2:]

Close=ChinaUnicom.Close
High=ChinaUnicom.High
Low=ChinaUnicom.Low

upboundDC=pd.Series(0.0,index=Close.index)
downboundDC=pd.Series(0.0,index=Close.index)
midboundDC=pd.Series(0.0,index=Close.index)

days=80
for i in range(days,len(Close)):
    upboundDC[i]=max(High[(i-days):i])
    downboundDC[i]=min(Low[(i-days):i])
    midboundDC[i]=0.5*(upboundDC[i]+downboundDC[i])

upboundDC=upboundDC[days:]
downboundDC=downboundDC[days:]
midboundDC= midboundDC[days:]

plt.rcParams['font.sans-serif'] = ['SimHei']
plt.plot(Close['2013'],label="Close",color='k')
plt.plot(upboundDC['2013'],label="upboundDC",color='b',linestyle='dashed')
plt.plot(midboundDC['2013'],label="midboundDC",color='r',linestyle='-.')
plt.plot(downboundDC['2013'],label="downboundDC",color='b',linestyle='dashed')
plt.title("2013年中国联通股价唐奇安通道")
plt.ylim(2.9,3.9)
plt.legend()

def upbreak(tsLine,tsRefLine):
    n=min(len(tsLine),len(tsRefLine))
    tsLine=tsLine[-n:]
    tsRefLine=tsRefLine[-n:]
    signal=pd.Series(0,index=tsLine.index)
    for i in range(1,len(tsLine)):
        if all([tsLine[i]>tsRefLine[i],tsLine[i-1]<tsRefLine[i-1]]):
            signal[i]=1
    return(signal)

def downbreak(tsLine,tsRefLine):
    n=min(len(tsLine),len(tsRefLine))
    tsLine=tsLine[-n:]
    tsRefLine=tsRefLine[-n:]
    signal=pd.Series(0,index=tsLine.index)
    for i in range(1,len(tsLine)):
        if all([tsLine[i]<tsRefLine[i],tsLine[i-1]>tsRefLine[i-1]]):
            signal[i]=1
    return(signal)

#DC Strategy
UpBreak=upbreak(Close[upboundDC.index[0]:],upboundDC)
DownBreak=downbreak(Close[downboundDC.index[0]:],\
          downboundDC)
BreakSig=UpBreak-DownBreak

tradeSig=BreakSig.shift(1)
ret=Close/Close.shift(1)-1
tradeRet=(ret*tradeSig).dropna()
tradeRet[tradeRet==-0]=0
winRate=len(tradeRet[tradeRet>0]\
            )/len(tradeRet[tradeRet!=0])
    
print(winRate)

