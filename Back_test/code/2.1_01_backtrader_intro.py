# -*- coding: utf-8 -*-
"""
Created on Wed Oct 27 16:40:14 2021

@author: 52207
"""

#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @license : (C) Copyright 2017-2020.
# @Time    : 2020/5/23 13:32
# @File    : backtrade2.py
# @Software: PyCharm
# @desc    :
 
import pandas as pd
import backtrader as bt

import pymysql

from backtrader_plotting import Bokeh
from backtrader_plotting.schemes import Tradimo
 
#设置策略的完整量化程序
syblst=['002046.SZ','600663.SH']
baslst=['000001.SH']  #上证
sdate='20180101'
edate='20181231'
con = pymysql.connect(host='mysql.bizanaly.cn', port=3306, database='tushare', user='test',password='Aa123456', charset='utf8')
sql="select * from daily where ts_code in ('"+syblst[0]+"','"+syblst[1]+"') and trade_date>='"+sdate+"' and trade_date<='"+edate+"' \
    union all  select * from index_daily where ts_code in ('"+baslst[0]+"') and trade_date>='"+sdate+"' and trade_date<='"+edate+"'"
df=pd.read_sql(sql,con)
#con.close()

df['trade_date'] = pd.to_datetime(df['trade_date'])
# df = df.drop(['change', 'pre_close', 'pct_chg', 'amount'], axis=1)
df = df.rename(columns={'vol': 'volume'})
df.set_index('trade_date', inplace=True)  # 设置索引覆盖原来的数据
df = df.sort_index(ascending=True)  # 将时间顺序升序，符合时间序列

dataframe = df
dataframe['openinterest'] = 0
data1 = bt.feeds.PandasData(dataname=dataframe[dataframe['ts_code']==syblst[0]])
data2 = bt.feeds.PandasData(dataname=dataframe[dataframe['ts_code']==syblst[1]])
data3 = bt.feeds.PandasData(dataname=dataframe[dataframe['ts_code']==baslst[0]])
# 添加数据
cerebro = bt.Cerebro()
cerebro.adddata(data1,name=syblst[0])
cerebro.adddata(data2,name=syblst[1])    
cerebro.adddata(data3,name=baslst[0])    

#创建一个：最简单的MA均线策略类class
class ma(bt.Strategy):
    # 定义MA均线策略的周期参数变量，默认值是15
    # 增加类一个log打印开关变量： fgPrint，默认自是关闭
    params = (('period', 15),('fgPrint', False), )

        
    def log(self, txt, dt=None, fgPrint=False):
        # 增强型log记录函数，带fgPrint打印开关变量
        if self.params.fgPrint or fgPrint:
            dt = dt or self.datas[0].datetime.date(0)
            print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self,vdict={}):
        # 默认数据，一般使用股票池当中，下标为0的股票，
        # 通常使用close收盘价，作为主要分析数据字段
        self.dataclose = self.datas[0].close
        #
        #
        if len(vdict)>0:
            self.p.period=int(vdict.get('period'))
            

        # 跟踪track交易中的订单（pending orders），成交价格，佣金费用
        self.order = None
        self.buyprice = None
        self.buycomm = None
        
        # 增加一个均线指标：indicator
        # 注意，参数变量period，主要在这里使用
        self.sma = bt.indicators.SimpleMovingAverage(
            self.datas[0], period=self.params.period)

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
                self.log('卖单执行SELL EXECUTED,成交价： %.2f,小计 Cost: %.2f,佣金 Comm %.2f'  
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
        self.log('当前收盘价Close, %.2f' % self.dataclose[0])
        #
        #
        # 检查订单执行情况，默认每次只能执行一张order订单交易，可以修改相关参数，进行调整
        if self.order:
            return
        #
        # 检查当前股票的仓位position
        if not self.position:
            #
            # 如果该股票仓位为0 ，可以进行BUY买入操作，
            # 这个仓位设置模式，也可以修改相关参数，进行调整
            #
            # 使用最简单的MA均线策略
            if self.dataclose[0] > self.sma[0]:
                # 如果当前close收盘价>当前的ma均价
                # ma均线策略，买入信号成立:
                # BUY, BUY, BUY!!!，买！买！买！使用默认参数交易：数量、佣金等
                self.log('设置买单 BUY CREATE, %.2f, name : %s' % (self.dataclose[0],self.datas[0]._name))

                # 采用track模式，设置order订单，回避第二张订单2nd order，连续交易问题
                self.order = self.buy()
                
        else:
            # 如果该股票仓位>0 ，可以进行SELL卖出操作，
            # 这个仓位设置模式，也可以修改相关参数，进行调整
            # 使用最简单的MA均线策略
            if self.dataclose[0] < self.sma[0]:
                # 如果当前close收盘价<当前的ma均价
                # ma均线策略，卖出信号成立:
                # 默认卖出该股票全部数额，使用默认参数交易：数量、佣金等
                self.log('SELL CREATE, %.2f, name : %s' % (self.dataclose[0],self.datas[0]._name))

                # 采用track模式，设置order订单，回避第二张订单2nd order，连续交易问题
                self.order = self.sell()        

    def stop(self):
        # 新增加一个stop策略完成函数
        # 用于输出执行后带数据
        self.log('(策略参数 Period=%2d) ，最终资产总值： %.2f' %
                 (self.params.period, self.broker.getvalue()), fgPrint=True)


# 将交易策略加载到回测系统中
cerebro.addstrategy(ma)
# 设置初始资本为100,000
cerebro.broker.setcash(100000.0)
# 每次固定交易数量
cerebro.addsizer(bt.sizers.FixedSize, stake=1000)
# 手续费
cerebro.broker.setcommission(commission=0.0025)
 
print('初始资金: %.2f' % cerebro.broker.getvalue())
#cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe') 
#timeframe=bt.TimeFrame.Days, 
cerebro.addanalyzer(bt.analyzers.SharpeRatio, timeframe=bt.TimeFrame.Days, \
                    riskfreerate=0.003, annualize=True, _name='sharpe')
cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
cerebro.addanalyzer(bt.analyzers.Returns, _name = "returns")

results = cerebro.run()
strat = results[0]
x1=results[0].analyzers.returns.get_analysis()['rnorm100']
x2=results[0].analyzers.drawdown.get_analysis()['max']['drawdown']
x3=results[0].analyzers.sharpe.get_analysis()['sharperatio']
#backtrader_plotting

print('最终资金: %.2f' % cerebro.broker.getvalue())
print('夏普比率:',x3)
print('回撤指标:',x2)
print('收益指标:',x1)

b = Bokeh(style='bar', plot_mode='single', output_mode='save',show=True,filename='2.1_01_backtrader_intro.html',scheme=Tradimo())
cerebro.plot(b)
