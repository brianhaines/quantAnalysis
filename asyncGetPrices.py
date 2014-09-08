#! /usr/bin/env python3
'''This sript will concurrently request prices from my 
price server app and return the responses as a list of dicts'''

import asyncio  
import aiohttp
from datetime import datetime
import cleanHistory as ch
import pandas as pd


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
    tickers = ['XOM','CVX','BP','SPY','XLE']
    nPrices = 3000

    urls=[]
    for each in tickers:
    	s = url+each+'&'+str(nPrices)
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

    # for each in resList:
    #     print(each['Ticker'])

    #Convert all those numbers to a clean pandas dataFrame
    outFrame = ch.cleaner(resList)
    
    # Regression
    # from pandas.stats.api import ols
    # res = ols(y=outFrame['XOM'],x=outFrame['CVX'])
    # print(res)
    # Run some regressions
    print(outFrame.cov())
    # print(outFrame)
    # rollMean = pd.rolling_mean(outFrame['XOM'],60)
    # pd.rolling_corr(outFrame.XOM,outFrame.CVX,50).plot(style='k')

    correls = pd.rolling_corr(outFrame.XOM,outFrame.CVX, 50,pairwise=True)
    print(correls)
    # print(outFrame.XOM)
    # print(outFrame.DateTime.min(), rollCorr.min())