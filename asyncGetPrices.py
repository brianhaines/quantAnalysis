#! /usr/bin/env python3
'''This sript will concurrently request prices from my 
price server app and return the responses as a list of dicts'''

import asyncio  
import aiohttp
from datetime import datetime
import cleanHistory as ch
import pandas as pd
import matplotlib.pyplot as plt
import statsmodels.api as sm
import statsmodels.tsa.stattools as ts
# For Hurst Exponent
from numpy import cumsum, log, polyfit, sqrt, std, subtract
from numpy.random import randn

resList=[]

def hurstTest(ts):
    ''' Returns the Hust Exponent of the given time series.'''
    # Create a range of lagged values
    lags = range(2, 100)

    # Calculate the array of the variances of the lagged differences
    tau = [sqrt(std(subtract(ts[lag:], ts[:-lag]))) for lag in lags]

    # Use a linear fit to estimate the Hurst Exponent
    poly = polyfit(log(lags), log(tau), 1)

    # Return the Hurst exponent from the polyfit output
    return poly[0]*2.0


def fetch_page(url, idx):
    global resList
    r = []
    response = yield from aiohttp.request('GET', url)
    # r = yield from response.read_and_close()
    r = yield from response.json()
    
    resList.append(r)
    return (r)

def main():  
    url = 'http://yahooserver.herokuapp.com/prices/'
    tickers = ['SPY','XOM','CVX','BP','XLE']
    nPrices = 8000

    urls=[]
    for each in tickers:
    	s = ''.join([url,each,'&',str(nPrices)])
    	urls.append(s)

    coros = []
    for idx, url in enumerate(urls):
        coros.append(asyncio.Task(fetch_page(url, idx)))
    yield from asyncio.gather(*coros)


if __name__ == '__main__':  
    t = (datetime.now())
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    print('Response took: ', datetime.now()-t, 'seconds.')

    #Convert all those numbers to a clean pandas dataFrame
    outFrame = ch.cleaner(resList)
    
    # Construct a regression between two stocks
    stk_y = 'XOM'
    stk_x = 'CVX'
    window = 100

    # Make a frame for a pair
    pairFrame = pd.DataFrame(index=outFrame.index)
    pairFrame['DateTime'] = outFrame['DateTime']
    pairFrame['stk_y'] = outFrame[stk_y]
    pairFrame['stk_x'] = outFrame[stk_x]
    pairFrame['stk_y_ret'] = pairFrame['stk_y'][1:]/pairFrame['stk_y'][:-1].values-1
    pairFrame['stk_x_ret'] = pairFrame['stk_x'][1:]/pairFrame['stk_x'][:-1].values-1
    
    # Rolling linear regression model    
    model2 = pd.ols(y=pairFrame['stk_y_ret'],x=pairFrame['stk_x_ret'],window=window)

    # Add the hedge ratio to pairFrame
    ## Because beta is the only result parameter used, the beta identity of:
    ## Beta = Cov(X,Y)/var(y) can be substituted.
    pairFrame['hedge_ratio']=model2.beta['x']
    pairFrame['hedge_ratio'] = pd.rolling_mean(pairFrame['hedge_ratio'],10)
    pairFrame= pairFrame.dropna()
    # Calculate the price spread between the stocks
    pairFrame['spread'] = pairFrame['stk_y'] - pairFrame['hedge_ratio']*pairFrame['stk_x']
    pairFrame['z_score'] = (pairFrame['spread'] - pd.rolling_mean(pairFrame['spread'],window=window))/pd.rolling_std(pairFrame['spread'],window=window)

    # Error check the dataFrame
    print('PairFrame')
    print(pairFrame.head())
    print(pairFrame.tail())

    # Plot the spread.
    plt.plot(pairFrame['spread'],'b-',pd.rolling_mean(pairFrame['spread'],window=window),'r--')

    # The Statsmodels paradigm for OLS
    y = outFrame[stk_y]
    x = outFrame[stk_x]
    X = sm.add_constant(x)
    model = sm.OLS(y, X)
    OLSresults = model.fit()
    # print(OLSresults.params[1])
    # print(OLSresults.summary())

    # Adjusted Dickey Fuller test
    adfOut = ts.adfuller(pairFrame['spread'], 10)  
    print()
    print('Calculated ADF Test Statistic:', adfOut[0])
    for k, v in adfOut[4].items():        
        if adfOut[0]<v:
            print('The series is likely to be mean reverting at ', k, '(',round(v,3),')',' confidence.')
            # print('The series passes the ADF Test at ', k, '(',round(v,3),')', ' confidence. Likely mean reverting.')
        elif adfOut[0]>v:
            # print('The series failed to pass the ADF Test at ', k, '(',round(v,3),')', ' confidence. Not likely to be mean reverting.')
            print('The series is unlikely to be mean reverting at ', k, '(',round(v,3),')',' confidence.')

    ##### Hurst Exponent test for stationarity ######
    # Create a Gometric Brownian Motion, Mean-Reverting and Trending Series
    gbm = log(cumsum(randn(100000))+1000)
    mr = log(randn(100000)+1000)
    tr = log(cumsum(randn(100000)+1)+1000)

    # Output the Hurst Exponent for each of the above series
    print('')
    print('Husrt Test')
    print('Hurst(Brownian Motion): ',hurstTest(gbm))
    print('Hurst(Mean Reversion): ',hurstTest(mr))
    print('Hurst(Trending): ',hurstTest(tr))

    # Using the spread calculated above in pairFrame
    print('Hurst(Spread1): ', hurstTest(pairFrame['spread']))

    # Generate the plots
    # plt.plot(y,'b--',x,'r--')
    # plt.plot(diff,'b--', mean_diff, 'r--', mean_diff2, 'g--')
    plt.show()