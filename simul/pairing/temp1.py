import calendar
import pandas as pd
import os.path
import numpy as np
import datetime
import logging


data_path=os.path.dirname(__file__)+'/'


logging.info('starting ...')

flights_df = pd.read_csv(data_path+"flight_pairing.csv")
flights_df.drop(flights_df.filter(regex="Unname"),axis=1, inplace=True)






'''

final_df=pd.DataFrame()
flights_df['dtyRepTmUTC'] = pd.to_datetime(flights_df['dtyRepTmUTC'])
flights_df['dtyRelTmUTC'] = pd.to_datetime(flights_df['dtyRelTmUTC'])
pairing_id=1
new_duty_id=1
flights_df['pairingId']=''
flights_df['totPairingUTC']=''

last_new_duty_id=flights_df.loc[len(flights_df)-1,'newDutyId']

while new_duty_id < last_new_duty_id :
    df=flights_df[flights_df['newDutyId'].isin([new_duty_id])]
    df=df.append(flights_df[flights_df['newDutyId'].isin([new_duty_id+1])])
    df['pairingId']=pairing_id
    h_i=df.head(1).index.tolist()[0]
    t_i=df.tail(1).index.tolist()[0]
    
    df['totPairingUTC']=df.loc[t_i,'dtyRelTmUTC']-df.loc[h_i,'dtyRepTmUTC']
    final_df=final_df.append(df)
    pairing_id+=1
    new_duty_id+=2

'''

'''
Create layover for the flight at the end of the duty if the duty ends not in staring base origin airport
and if the flight DestUTC falls between 8PM and 6AM. 
'''    
fa_bases=["ATL","HNL","CVG","SLC","LAX","MCO","BOS","EWR","JFK","LGA","MSP","SEA","DTW","MIA","FLL","SFO","PBI","SNA"]
    
final_df=pd.DataFrame()
pairing_id=1
new_duty_id=1
flights_df['layover']=''
hour_14=datetime.timedelta(hours=+14)
flights_df['totDutyTm'] = pd.to_timedelta(flights_df['totDutyTm'])
#flights_df['totDutyTm'] = pd.to_datetime(df['totDutyTm'], errors='coerce', format='%Y-%m-%d %H:%M:%S')
last_new_duty_id=flights_df['newDutyId'].max()
flights_df["DestUTC"] = pd.to_datetime(flights_df['DestUTC'])

while new_duty_id < last_new_duty_id :
    df=flights_df[flights_df['newDutyId'].isin([new_duty_id])]
    h_i=df.head(1).index.tolist()[0]
    t_i=df.tail(1).index.tolist()[0]
    
    dest_time_hour = df.loc[h_i,'DestUTC'].hour
    
    if df.loc[h_i,'Origin']!=df.loc[t_i,'Dest'] and (20 <= dest_time_hour or dest_time_hour <= 6 ):
        print("yes layover")
        #add layover=1 only the last flight in the duty
        df['layover']=0
        df.at[t_i,'layover']=1
    else:
        df['layover']=0
        
    final_df=final_df.append(df)
    new_duty_id+=1
    

    
    

final_df.to_csv("temp1.csv")


