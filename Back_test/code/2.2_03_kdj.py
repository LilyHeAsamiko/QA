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

class kdj_strategy(bt.Strategy):
    lines = ('K', 'D', 'J')

    params = (
        ('period', 9),
        ('period_dfast', 3),
        ('period_dslow', 3),
    )

    plotlines = dict(
        J=dict(
            _fill_gt=('K', ('red', 0.50)),
            _fill_lt=('K', ('green', 0.50)),
        )
    )

    def __init__(self):
        # Add a KDJ indicator
        self.kd = bt.indicators.StochasticFull(
            self.data,
            period=self.p.period,
            period_dfast=self.p.period_dfast,
            period_dslow=self.p.period_dslow,
        )

        self.K = self.kd.percD
        self.D = self.kd.percDSlow
        self.J = self.K * 3 - self.D * 2

    def next(self):
        condition1 = self.J[-1] - self.D[-1]
        condition2 = self.J[0] - self.D[0]
        
        if not self.position:
            # J - D 值

            if condition1 < 0 and condition2 > 0:
                #self.log("BUY CREATE, %.2f" % self.dataclose[0])
                self.order = self.buy()

        else:
            if condition1 > 0 and condition2 < 0:
                #self.log("SELL CREATE, %.2f" % self.dataclose[0])
                self.order = self.sell()

if __name__ == '__main__':
    con = pymysql.connect(host='mysql.bizanaly.cn', port=3306, database='tushare', user='tushare',password='etms2000', charset='utf8')

    # 创建策略容器
    cerebro = bt.Cerebro()
    # 添加自定义的策略RSI_SMA
    cerebro.addstrategy(kdj_strategy)

    stock_code = '002859.SZ'
    start_date='20200101'
    end_date='20201231'
    #df = pro.us_daily(ts_code=stock_code, start_date='20200101', end_date='20200828')
    sql="select * from daily where ts_code='"+stock_code+"' and trade_date>='"+start_date+"' and trade_date<='"+end_date+"'"
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
    b = Bokeh(style='bar', plot_mode='single', output_mode='save',show=True,filename='2.2_03_kdj.html',scheme=Tradimo())
    cerebro.plot(b)

