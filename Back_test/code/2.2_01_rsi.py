# -*- coding: utf-8 -*-
"""
Created on Thu Mar 10 01:31:03 2022

@author: 52207
"""

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import datetime
import pandas as pd
import backtrader as bt
import numpy as np
import pymysql

from backtrader_plotting import Bokeh
from backtrader_plotting.schemes import Tradimo

class RSI_SMA(bt.Strategy):
    params = (('short', 30),
              ('long', 70),)
 
    def __init__(self):
        self.rsi = bt.indicators.RSI_SMA(
            self.data.close, period=21)
 
    def next(self):
        if not self.position:
            if self.rsi < self.params.short:
                self.buy()
        else:
            if self.rsi > self.params.long:
                self.sell()


if __name__ == '__main__':
    con = pymysql.connect(host='mysql.bizanaly.cn', port=3306, database='tushare', user='tushare',password='etms2000', charset='utf8')

    # 创建策略容器
    cerebro = bt.Cerebro()
    # 添加自定义的策略RSI_SMA
    cerebro.addstrategy(RSI_SMA)

    stock_code = '002046.SZ'
    #df = pro.us_daily(ts_code=stock_code, start_date='20200101', end_date='20200828')
    sql="select * from daily where ts_code='"+stock_code+"' and trade_date>='20180101' and trade_date<='20181231'"
    df=pd.read_sql(sql,con)
    #con.close()
    
    df['trade_date'] = pd.to_datetime(df['trade_date'])
    # df = df.drop(['change', 'pre_close', 'pct_chg', 'amount'], axis=1)
    df = df.rename(columns={'vol': 'volume'})
    df.set_index('trade_date', inplace=True)  # 设置索引覆盖原来的数据
    df = df.sort_index(ascending=True)  # 将时间顺序升序，符合时间序列

    dataframe = df
    dataframe['openinterest'] = 0
    data = bt.feeds.PandasData(dataname=dataframe)
    # 添加数据
    codename=stock_code
    cerebro.adddata(data,name=codename)
    # 设置资金
    cerebro.broker.setcash(100000.0)
    # 设置每笔交易交易的股票数量
    cerebro.addsizer(bt.sizers.FixedSize, stake=10)
    # 设置手续费
    cerebro.broker.setcommission(commission=0.001)
    # 输出初始资金
    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())
    # 运行策略
    cerebro.run()
    # 输出结果
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())
    b = Bokeh(style='bar', plot_mode='single', output_mode='save',show=True,filename='2.2_01_rsi.html',scheme=Tradimo())
    cerebro.plot(b)

