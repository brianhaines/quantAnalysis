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


resList=[]

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
    tickers = ['SPY','XOM','CVX']#,'BP','XLE']
    nPrices = 5000

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
    y = outFrame['XOM']
    x = outFrame['CVX']
    X = sm.add_constant(x)
    model = sm.OLS(y, X)
    OLSresults = model.fit()

    # Use the beta of the regression to weight the pairs spread calculation
    diff = outFrame['XOM']-(OLSresults.params[1]*outFrame['CVX'])
    mean_diff = pd.rolling_mean(diff, 50)
    mean_diff2 = pd.rolling_mean(diff, 100)

    # print(OLSresults.params[1])
    print(OLSresults.summary())

    # Error Checking the time series
    # print(outFrame[['DateTime','XOM']].head())
    # print(outFrame[['DateTime','XOM']].tail(5))

    # Generate the plots
    # plt.plot(y,'b--',x,'r--')
    plt.plot(diff,'b--', mean_diff, 'r--', mean_diff2, 'r-')
    plt.show()