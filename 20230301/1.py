# 
"""
Created on Fri Aug 16 10:51:48 2024
全国统一考试模拟题 202303
@author: Admin
"""
#1.1 为了检验这两个期货指数是否适合进行配对交易，该研究员准备使用训练集数据进行相关性检查，请你使用training1 training2 中的数据，绘制两个期货指数的价格走势图，并计算秩相关系数。（
import pandas as pd
#import numpy as np
training1=pd.read_csv(r"E:\AQF\20230301\training1.csv",parse_dates=True,index_col=0)
training2=pd.read_csv(r"E:\AQF\20230301\training2.csv",parse_dates=True,index_col=0)
training = pd.merge(training1,training2,left_index =True,right_index=True,suffixes =('_1','_2'))
#training.plot(figsize = (8,6))
#training.corr(method = 'spearman')
import matplotlib.pyplot as plt
from scipy import *
plt.figure()
plt.plot(training1['trade_date'],training1['close'])
plt.plot(training2['trade_date'],training2['close'])
plt.legend(['training1','training2'])
#np.correlate(training['close_1'],training['close_2'])
df = pd.DataFrame(training)
corr_spearman_matrix = df.corr(method='spearman')
#corr,p_value = stats.pearsonr(df['close_1'],df['close_2'])
corr,p_value = stats.spearmanr(df['close_1'],df['close_2'])

#1.2
training['spread'] = training['close_1']-training['close_2']
mu = training['spread'].mean()
sigma = training['spread'].std()
test = pd.read_csv(r"E:\AQF\20230301\test.csv",parse_dates=True,index_col=0)
test['spread'] = test['close_1']-test['close_2']
test['up'] = mu+2*sigma
test['down'] = mu-2*sigma
test['position_1'] = np.where(test['spread']>test['up'],-1,0)
test['position_2'] = np.where(test['spread']<test['down'],1,test['position_1'])
test['position_2'] = -test['position_2']

#2
#factor = pd.read_csv(r"E:\AQF\20230301\factor.csv",index_col='trade_date',parse_dates=['trade_date'])
factor = pd.read_csv(r"E:\AQF\20230301\factor.csv",parse_dates=['trade_date'])
factor['trade_date'] = pd.to_datetime(factor['trade_date'],format='%Y%m%d')
factor['roe'] /= 100
factor.set_index('trade_date',inplace=True)
returns = pd.read_csv(r"E:\AQF\20230301\returns.csv",index_col='trade_date',parse_dates=True)
#returns['trade_date'] = pd.to_datetime(returns['trade_date'],format='%Y%m%d')
data =pd.merge(factor.loc['2022-01'],returns.loc['2022-01'])
from sklearn.linear_model import LinearRegression
x = factor['roe']
y = returns['pct_chg']
X = np.array(x).reshape(-1,1)
Y = np.array(y).reshape(-1,1)
lm = LinearRegression()
lm.fit(X,Y)

print(f'Intercept:{lm.intercept_}')
print(f'Slope:{lm.coef_[0]}')
print(f'Score:{lm.score(X,Y)}')

plt.scatter(X,Y,label='Data points on 2022')
plt.plot(X,model.predict(X),color='red',label='Fitted Line')
plt.xlabel('roe')
plt.ylabel('pct_chg')
plt.title('Linear Regression using scikit-learn')
plt.legend()
plt.show()

data =pd.DataFrame(np.array([list(factor.loc['2022']['roe']),list(returns.loc['2022']['pct_chg'])]).transpose(),index =['2022-01']*5)
import statsmodels.api as sm
xx = sm.add_constant(data.iloc[:,0])
est =sm.OLS(data.iloc[:,1],xx).fit()
est.summary()

'''
                            OLS Regression Results                            
==============================================================================
Dep. Variable:                      1   R-squared:                       0.066
Model:                            OLS   Adj. R-squared:                 -0.246
Method:                 Least Squares   F-statistic:                    0.2109
Date:                Sat, 17 Aug 2024   Prob (F-statistic):              0.677
Time:                        00:50:02   Log-Likelihood:                 9.8146
No. Observations:                   5   AIC:                            -15.63
Df Residuals:                       3   BIC:                            -16.41
Df Model:                           1                                         
Covariance Type:            nonrobust                                         
==============================================================================
                 coef    std err          t      P>|t|      [0.025      0.975]
------------------------------------------------------------------------------
const         -0.0686      0.051     -1.350      0.270      -0.230       0.093
0              0.3371      0.734      0.459      0.677      -1.999       2.673
==============================================================================
Omnibus:                          nan   Durbin-Watson:                   3.188
Prob(Omnibus):                    nan   Jarque-Bera (JB):                0.079
Skew:                           0.140   Prob(JB):                        0.961

est.pvalues
Out[408]: 
const    0.269835
0        0.677288
dtype: float64

est.params
Out[409]: 
const   -0.068642
0        0.337109
dtype: float64
'''

import scipy.stats as stats
f_stat,p_value = stats.f_oneway(X,Y)
results =stats.linregress(x,y) # sl,intercpt,r_val,p_val,std_err
print(results)
'''
LinregressResult
(slope=0.3371092099733863, 
 intercept=-0.06864202015756132, 
 rvalue=0.2562913169053877, 
 pvalue=0.6772882154162738, 
 stderr=0.7340450306002909, 
 intercept_stderr=0.050845430883583544)
'''

#
factors = pd.read_csv(r"E:\AQF\20230301\factors.csv",parse_dates=True,index_col=0)
df = pd.merge(factor.loc['2022-01-04'],returns.loc['2022-01-23'],left_on = '2022-01-04',right_on='2022-01-23',how='inner')
df = pd.concat([factor.loc['2022-01-04'],returns.loc['2022-01-23']])
df = df.fillna(value=0)
#！！！！df.ffill().bfill()
result = pd.DataFrame(columns= ['significant','direction']) 
for d in [4,23]:
    dstring = f'2022-01-{d:02}'
    x=df['roe']
    y=df['pct_chg']
    est=sm.OLS(y,x).fit()
    significant=(est.pvalues['roe']<0.05)
    direction = np.sign(est.params['roe'])
    result.loc[dstring] = significant,direction
    
#3
future = pd.read_csv(r"E:\AQF\20230301\future.csv",parse_dates=True)
future['trade_date'] = pd.to_datetime(future['trade_date'],format='%Y/%m/%d')
future = future.set_index(['trade_date'])
future.sort_index(inplace=True)
future['MA3'] = future['close'].rolling(3).mean()
future['MA5'] = future['close'].rolling(5).mean()
'''
双均线交易策略：当3日均线上穿5日均线时，看多；当3日均线下穿5日均线时，看空；
'''
future['position'] = np.where(future['MA3']>future['MA5'],1,-1) 
future.loc[future['MA3'].isna()|future['MA5'].isna(),'position']=0 

future['position'].plot(ylim=[-1.1,1.1],title='Market Positioning',figsize=(16,8))
plt.show()
#
df = pd.read_csv(r"E:\AQF\20230301\stock_data.csv",parse_dates=True)
#(close-close.shift)/close.shift= returns
#df['close'] = 7.25*(df['returns']+1).cumprod()
#df.loc[0,'close'] = 7.25
df['close'] = 7.25*(df['returns'].fillna(0)+1).cumprod()

#4.2
M=10000
N=100
T=1
dt=T/N
simulated_price = np.zeros((M,1))
close_p = df['close'].values
#returns = np.log(close_p.shift(-1).ffill()/close_p)
returns = np.log(close_p[1:]/close_p[:-1])
mean_p = np.mean(returns)
std_p = np.std(returns)
for i in range(M):
    S = close_p[-1]
    for j in range(N):
        S *= (1+mean_p*dt +std_p*dt**0.5*np.random.normal())
        simulated_price[i-1] = S
        
simulated_return = np.log(simulated_price/close_p[-1])
VaR_95 = np.percentile(simulated_return,5)
VaR_99 = np.percentile(simulated_return,1)
print('95%VaR:{:.4%}'.format(VaR_95))
print('99%VaR:{:.4%}'.format(VaR_99))
'''
simulated_return = (simulated_price-close_p)/close_p
VaR_95 = np.percentile(np.mean(simulated_return,0),5)
VaR_99 = np.percentile(np.mean(simulated_return,0),1)
print('95%VaR:{:.4%}'.format(VaR_95))
print('99%VaR:{:.4%}'.format(VaR_99))
'''

#5
def standardize(x):
    return (x-x.mean())/x.std()

data_x = pd.read_csv(r"E:\AQF\20230301\data_x.csv",index_col = 0)
data_2=standardize(data_x)

data_y = pd.read_csv(r"E:\AQF\20230301\data_y.csv",index_col = 0)
data_3=np.sign(data_y)

from sklearn.model_selection import train_test_split
train_x,test_x,train_y,test_y  = train_test_split(data_2,data_3.values.flatten(),test_size=0.2)
from sklearn import *
clf_DT = tree.DecisionTreeClassifier()
model = clf_DT.fit(train_x,train_y)

predict_y =model.predict(test_x)

accuracy=(test_y==predict_y).sum()/len(test_y)