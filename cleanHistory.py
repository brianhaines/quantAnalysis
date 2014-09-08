'''This file does the work of combining the returned price series. 
The reurned panadas dataframe will contain only those price buckets
that are common between the series being analysed.'''

from datetime import datetime
import numpy as np
import pandas as pd

def cleaner(pList):
    if len(pList)<2:
        raise Exception("Need at least two stocks!")
    
    labels = ['DateTime']

    for sid, series in enumerate(pList):
        if sid == 0:
            #Make the initial series
            d1=[]
            v1=[]
            for i in series['Prices']:
                d1.append(''.join([i[0],'T',i[1]]))
                v1.append(i[2])
            a1 = np.array([d1,v1])
            dfOut=pd.DataFrame(a1).T
            labels.append(series['Ticker'])
            dfOut.columns = ['DateTime',series['Ticker']]            
        elif sid > 0:
            #Make a new dataframe for each subsequent series
            dN=[]
            vN=[]
            for i in series['Prices']:
                dN.append(''.join([i[0],'T',i[1]]))
                vN.append(i[2])
            aN = np.array([dN,vN])
            dfN=pd.DataFrame(aN).T
            labels.append(series['Ticker'])
            dfN.columns = ['DateTime',series['Ticker']]
            #Now we have the initial and Nth series in dataframe format

            # This will merge the Nth df with the initial df
            dfOut = pd.DataFrame(np.array(dfOut.merge(dfN, on='DateTime', how='outer').sort('DateTime'),),columns=labels)

    # All of the stocks have been added to the dataframe, now clean it up
    dfClean = dfOut.dropna()
    
    labels.pop(0)
    dfClean[labels] = dfClean[labels].astype(float) #This raises a soft warning.
    #Trying to change price values dtype to float. The line above works but raises an error:
    #     "A value is trying to be set on a copy of a slice from a DataFrame.
    #     "Try using .loc[row_index,col_indexer] = value instead
    # Below are attempts to reassign dtypes without getting an error.
    # print(dfClean.dtypes)
    # dfClean.loc[dfClean[:,labels]] = dfClean[:,labels].astype(float)
    # dfClean.iloc[dfClean[:,:]].astype(float)
    # dfClean.loc[dfClean[:,labels]].astype(float)
    # print(dfClean.dtypes)
        
    # dfClean['diff'] = dfClean[pList[1]['Ticker']].sub(dfClean[pList[0]['Ticker']], axis=0)    

    return(dfClean)