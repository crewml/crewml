import itertools
import pandas as pd
import os.path
import numpy as np
import datetime


data_path=os.path.dirname(__file__)+'/'






def calculateDuty(df):    
    df.reset_index(drop=True,inplace=True) 
    flights_df['dtyRepTmUTC'] = pd.to_datetime(flights_df['dtyRepTmUTC'])
    flights_df['dtyRelTmUTC'] = pd.to_datetime(flights_df['dtyRelTmUTC'])
    ind=0
    duty_id=1
    hours_6=datetime.timedelta(hours=+6)
    all_df=pd.DataFrame()
    
    for i, g_df in df.groupby(df.index // 2):
        if g_df.loc[ind]['dtyRelTmUTC'] - g_df.loc[ind]['dtyRepTmUTC'] > hours_6:
            g_df.at[ind,'dutyId']= duty_id
            g_df.at[ind+1,'dutyId']= duty_id+1
            duty_id+=2
        else:
            g_df['dutyId']= duty_id
            duty_id+=1

        all_df=all_df.append(g_df)
        ind+=2
        
    return all_df            
    


flights_df = pd.read_csv(data_path+"b2b.csv")
flights_df.drop(flights_df.filter(regex="Unname"),axis=1, inplace=True)

df=calculateDuty(flights_df)
df.to_csv("temp2.csv")

