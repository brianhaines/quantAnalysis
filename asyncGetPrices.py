#! /usr/bin/env python3
'''This sript will concurrently request prices from my 
price server app and return the responses as a list of dicts'''

import asyncio  
import aiohttp
from datetime import datetime
import cleanHistory as ch


resList=[]

def fetch_page(url, idx):
    global resList
    r = []
    response = yield from aiohttp.request('GET', url)
    r = yield from response.read_and_close()
    r = yield from response.json()
    resList.append(r)
    return (r)

def main():  
    url = 'http://yahooserver.herokuapp.com/prices/'
    tickers = ['XOM','CVX']
    nPrices = 500


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

    for each in resList:
        print(each['Ticker'])

    outFrame = ch.cleaner(resList)
    print(outFrame)

