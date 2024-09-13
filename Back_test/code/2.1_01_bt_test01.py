# -*- coding: utf-8 -*-
"""
Created on Tue Apr 11 17:16:24 2023

@author: 52207
"""

import backtrader as bt

#没有设置策略的量化核心代码
print('\n#1,设置BT量化回溯程序入口')
cerebro = bt.Cerebro()

print('\n#2,设置BT回溯初始参数：起始资金等')
dmoney0=100000.0
cerebro.broker.setcash(dmoney0)
dcash0=cerebro.broker.startingcash

print('\n#3,调用BT回溯入口程序，开始执行run量化回溯运算')
cerebro.run()

print('\n#4,完成BT量化回溯运算')
dval9=cerebro.broker.getvalue()   
print('\t起始资金 Starting Portfolio Value: %.2f' % dcash0)
print('\t资产总值 Final Portfolio Value: %.2f' % dval9)

#因没有设置策略，所以没有交易数据，故注释了最后图表生成语句
#print('\n#9,绘制BT量化分析图形')
#cerebro.plot()

