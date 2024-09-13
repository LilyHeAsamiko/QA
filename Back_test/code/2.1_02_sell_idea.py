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

        # 跟踪track交易中的订单（pending orders）
        self.order = None
        
    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # 检查订单执行状态order.status：
            # Buy/Sell order submitted/accepted to/by broker 
            # broker经纪人：submitted提交/accepted接受,Buy买单/Sell卖单
            # 正常流程，无需额外操作
            return

        # 检查订单order是否完成
        # 注意: 如果现金不足，经纪人broker会拒绝订单reject order
        # 可以修改相关参数，调整进行空头交易
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log('买单执行BUY EXECUTED, 报价：%.2f' % order.executed.price)
            elif order.issell():
                self.log('卖单执行SELL EXECUTED,报价： %.2f' % order.executed.price)

            self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('订单Order： 取消Canceled/保证金Margin/拒绝Rejected')

        # 检查完成，没有交易中订单（pending order）
        self.order = None
    
    def next(self):
        # 调用log函数，输出BT回溯过程当中，工作节点数据包BAR，对应的close收盘价
        self.log('收盘价Close, %.2f' % self.dataclose[0])
        # 检查订单执行情况，默认每次只能执行一张order订单交易，可以修改相关参数，进行调整
        if self.order:
            return
        # 检查当前股票的仓位position
        if not self.position:
            # 如果该股票仓位为0 ，可以进行BUY买入操作，
            # 这个仓位设置模式，也可以修改相关参数，进行调整
            # 使用经典的"三连跌"买入策略
            if self.dataclose[0] < self.dataclose[-1]:
                # 当前close价格，低于昨天（前一天，[-1]）
                if self.dataclose[-1] < self.dataclose[-2]:
                    # 昨天的close价格（前一天，[-1]），低于前天（前两天，[-2]）
                    # "三连跌"买入信号成立:
                    # BUY, BUY, BUY!!!，买！买！买！使用默认参数交易：数量、佣金等
                    self.log('设置买单 BUY CREATE, %.2f' % self.dataclose[0])
                    # 采用track模式，设置order订单，回避第二张订单2nd order，连续交易问题
                    self.order = self.buy()
        else:
            # 如果该股票仓位>0 ，可以进行SELL卖出操作，
            # 此处使用经验参数：
            # 前个订单，执行完成，5个周期后才能进行SELL卖出操作
            if len(self) >= (self.bar_executed + 5):
                # SELL, SELL, SELL!!! 卖！卖！卖！
                # 默认卖出该股票全部数额，使用默认参数交易：数量、佣金等
                self.log('设置卖单SELL CREATE, %.2f' % self.dataclose[0])

                # 采用track模式，设置order订单，回避第二张订单2nd order，连续交易问题
                self.order = self.sell()


#----------


if __name__ == '__main__':
    con = pymysql.connect(host='120.55.69.170', port=3306, database='tushare', user='tushare',password='etms2000', charset='utf8')

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
    b = Bokeh(style='bar', plot_mode='single', output_mode='save',show=True,filename=r'E:\BaiduNetdiskDownload\AQF\AQF课件\回测讲义\代码\Sell卖出策略回测.html',scheme=Tradimo())
    #b = Bokeh(style='bar', plot_mode='single', scheme=Tradimo())
    cerebro.plot(b)
    #cerebro.plot()
