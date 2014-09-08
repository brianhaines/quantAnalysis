#! /usr/bin/env python3
'''This sript will concurrently request prices from my 
price server app and return the responses as a list of dicts'''

import asyncio  
import aiohttp
from datetime import datetime
import numpy as np
import pandas as pd

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
    url1 = 'http://yahooserver.herokuapp.com/prices/XOM&1000'
    url2 = 'http://yahooserver.herokuapp.com/prices/CVX&1000'
   
    urls = [url1,url2]

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
	   #  print(each)

