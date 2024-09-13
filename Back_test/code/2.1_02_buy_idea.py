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

#----------------------
# 创建一个自定义策略类class
class TQSta001(bt.Strategy):

    def log(self, txt, dt=None):
        # log记录函数
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        # 默认数据，一般使用股票池当中，下标为0的股票，
        # 通常使用close收盘价，作为主要分析数据字段
        self.dataclose = self.datas[0].close

    def next(self):
        # next函数是最重要的trade交易（运算分析）函数， 
        # 调用log函数，输出BT回溯过程当中，工作节点数据包BAR，对应的close收盘价
        self.log('收盘价Close, %.2f' % self.dataclose[0])
        #
        # 使用经典的"三连跌"买入策略
        if self.dataclose[0] < self.dataclose[-1]:
            # 当前close价格，低于昨天（前一天，[-1]）
            if self.dataclose[-1] < self.dataclose[-2]:
                # 昨天的close价格（前一天，[-1]），低于前天（前两天，[-2]）
                # "三连跌"买入信号成立:
                # BUY, BUY, BUY!!!，买！买！买！使用默认参数交易：数量、佣金等
                self.log('设置买单 BUY CREATE, %.2f' % self.dataclose[0])
                self.buy()




#----------


if __name__ == '__main__':
    con = pymysql.connect(host='mysql.bizanaly.cn', port=3306, database='tushare', user='tushare',password='etms2000', charset='utf8')

    # 创建策略容器
    cerebro = bt.Cerebro()
    # 添加自定义的策略TestStrategy
    cerebro.addstrategy(TQSta001)
    #pro = ts.pro_api(token)
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
    cerebro.addsizer(bt.sizers.FixedSize, stake=100)
    # 设置手续费
    cerebro.broker.setcommission(commission=0.01)
    # 输出初始资金
    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())
    # 运行策略
    cerebro.run()
    # 输出结果
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())
    b = Bokeh(style='bar', plot_mode='single', output_mode='save',show=True,filename='E:\BaiduNetdiskDownload\AQF\AQF课件\回测讲义\代码\2.1_02_buy_idea.html',scheme=Tradimo())
    #b = Bokeh(style='bar', plot_mode='single', scheme=Tradimo())
    cerebro.plot(b)
    #cerebro.plot()
