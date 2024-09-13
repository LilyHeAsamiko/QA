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
# 创建一个：最简单的MA均线策略类class
class TQSta001(bt.Strategy):
    #定义MA均线策略的周期参数变量，默认值是15
    params = (
        ('period_sma5', 5),
        ('period_sma20', 20)
    )

    def log(self, txt, dt=None):
        # log记录函数
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        # 默认数据，一般使用股票池当中，下标为0的股票，
        # 通常使用close收盘价，作为主要分析数据字段
        self.dataclose = self.datas[0].close

		#计算10日均线
        self.sma5 = bt.indicators.MovingAverageSimple(self.dataclose, period=self.params.period_sma5)
        # 计算30日均线
        self.sma20 = bt.indicators.MovingAverageSimple(self.dataclose, period=self.params.period_sma20)

        # 跟踪track交易中的订单（pending orders），成交价格，佣金费用
        self.order = None
        self.buyprice = None
        self.buycomm = None
        
        # 调用内部指标模块：indicator
        # 注意，参数变量maperiod，主要在这里使用
        # self.sma = bt.indicators.SimpleMovingAverage(
        #     self.datas[0], period=self.params.maperiod)

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
                self.log('买单执行BUY EXECUTED,成交价： %.2f,小计 Cost: %.2f,佣金 Comm %.2f' 
                         % (order.executed.price,order.executed.value,order.executed.comm))
                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
            elif order.issell():
                self.log('卖单执行SELL EXECUTED,成交价： %.2f,小计 Cost: %.2f,佣金 Comm %.2f'  
                         % (order.executed.price,order.executed.value,order.executed.comm))

            self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('订单Order： 取消Canceled/保证金Margin/拒绝Rejected')

        # 检查完成，没有交易中订单（pending order）
        self.order = None

    def notify_trade(self, trade):
        # 检查交易trade是关闭
        if not trade.isclosed:
            return

        self.log('交易操盘利润OPERATION PROFIT, 毛利GROSS %.2f, 净利NET %.2f' %
                 (trade.pnl, trade.pnlcomm))   

    def next(self):
        # next函数是最重要的trade交易（运算分析）函数， 
        # 调用log函数，输出BT回溯过程当中，工作节点数据包BAR，对应的close收盘价
        self.log('收盘价Close, %.2f' % self.dataclose[0])
        #
        #
        # 检查订单执行情况，默认每次只能执行一张order订单交易，可以修改相关参数，进行调整
        if self.order:
            return
        
        
		# 当今天的10日均线大于30日均线并且昨天的10日均线小于30日均线，则进入市场（买）
        if self.sma5[0] > self.sma20[0] and self.sma5[-1] < self.sma20[-1]:
        	# 判断订单是否完成，完成则为None，否则为订单信息
            if self.order:
                return
			
			#若上一个订单处理完成，可继续执行买入操作
            self.order = self.buy()
            
		# 当今天的10日均线小于30日均线并且昨天的10日均线大于30日均线，则退出市场（卖）
        elif self.sma5[0] < self.sma20[0] and self.sma5[-1] > self.sma20[-1]:
        	# 卖出
            self.order = self.sell()

        
#----------


if __name__ == '__main__':
    con = pymysql.connect(host='120.55.69.170', port=3306, database='tushare', user='tushare',password='etms2000', charset='utf8')

    # 创建策略容器
    cerebro = bt.Cerebro()
    # 添加自定义的策略TestStrategy
    cerebro.addstrategy(TQSta001)
    #pro = ts.pro_api(token)
    stock_code = '301047.SZ'
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
    b = Bokeh(style='bar', plot_mode='single', output_mode='save',show=True,filename='d:/sma.html',scheme=Tradimo())
    cerebro.plot(b)

