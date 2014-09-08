'''This file does the work of combining the returned price series. 
The reurned panadas dataframe will contain only those price buckets
that are common between the series being analysed.'''

from datetime import datetime
import numpy as np
import pandas as pd

def cleaner(pList):
    d1=[]
    v1=[]
    for i in pList[0]['Prices']:
        d1.append(i[0]+'T'+i[1])
        v1.append(i[2])
        a1 = np.array([d1,v1])
    df1=pd.DataFrame(a1).T

    d2=[]
    v2=[]
    for i in pList[1]['Prices']:
        d2.append(i[0]+'T'+i[1])
        v2.append(i[2])
        a2 = np.array([d2,v2])

    df2=pd.DataFrame(a2).T
    
    df1.columns = df2.columns = ['t','v']

    dfOut = pd.DataFrame(np.array(df1.merge(df2, on='t', how='outer').sort('t'),),columns=['time',pList[0]['Ticker'],pList[1]['Ticker']])

    dfClean = dfOut.dropna(subset = [pList[0]['Ticker'],pList[1]['Ticker']])

    dfClean[[pList[0]['Ticker'],pList[1]['Ticker']]] = dfClean[[pList[0]['Ticker'],pList[1]['Ticker']]].astype(float)
    # print(dfClean.dtypes)
    # dfClean['diff'] = dfClean[pList[1]['Ticker']].sub(dfClean[pList[0]['Ticker']], axis=0)    

    return(dfClean)
    print((datetime.now()-t)/10)