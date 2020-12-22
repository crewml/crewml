import pandas as pd
import os.path
import numpy as np
import datetime


data_path=os.path.dirname(__file__)+'/'


duty_id=1
def calculate_Duty(df):
    if(len(df) ==0):
        return
    
    df['OrgUTC'] = pd.to_datetime(df['OrgUTC'])
    df["DestUTC"] = pd.to_datetime(df['DestUTC'])
    
    final_temp_df=pd.DataFrame()
    df["newDutyId"]=""
    
    while(len(df)!=0):
        '''
        Iterate df with two rows at a time, E.g. ATL-HNL and HNL-ATL two flights considered as
        one unit
        '''        
        for i, g_df in df.groupby(df.index // 2):   
            temp1_df=df.loc[(df["Origin"]==g_df.iloc[0].Origin) & (df["Dest"]==g_df.iloc[0].Dest) ]
            temp2_df=df.loc[(df["Origin"]==g_df.iloc[1].Origin) & (df["Dest"]==g_df.iloc[1].Dest) ]
            temp_df=temp1_df.append(temp2_df)
            temp_df.sort_index(inplace=True)

            if len(temp_df)!=0:
                final_temp_df=final_temp_df.append(chunk_flights(temp_df))
                df=df[~df['fltID'].isin(final_temp_df.fltID)]
            else:
                continue

        final_temp_df=final_temp_df.append(df)
        df=df[~df['fltID'].isin(final_temp_df.fltID)]
                
    return final_temp_df

'''
This method combines flights that can be grouped into single duty. Only flights
with flight time less than 3 hours is considered for the grouping. If the flight
time is more than 3 hours, combining 4 flights will give total duty perid of 12+ hours this
vilotes our total duty period range from 8-12.

45 minutes added to start and end of every flight OrgUTC and DestUTC

We're also using 15 minutes for duty period begin and end.
'''        
def chunk_flights(df):
    hour_3=datetime.timedelta(hours=+3)
    min_15=datetime.timedelta(minutes=+15)
    split_hours=df.iloc[0].DestUTC - df.iloc[0].OrgUTC  
    if  split_hours > hour_3:
        return df
    hours=split_hours.seconds//3600
    mins=(split_hours.seconds//60)%60
    split_hours=float(str(hours)+"."+str(mins))
    tot_flts=round(14/split_hours)
    final_df=pd.DataFrame()
    temp_df=pd.DataFrame()
    i=0
    df_len=len(df)
    global duty_id
    print("duty_id=",duty_id)
    while i<df_len:
        flag=True
        for i, g_df in df.groupby(df.index // 2):
            if len(temp_df)==0:
                temp_df=temp_df.append(g_df)
            if g_df.iloc[0].OrgUTC-min_15 > temp_df.iloc[len(temp_df)-1].DestUTC+min_15:
                temp_df=temp_df.append(g_df)
                if len(temp_df) < tot_flts and g_df.iloc[0].FlightDate == temp_df.iloc[len(temp_df)-1].FlightDate:
                    continue
                else:
                    temp_df["newDutyId"]=duty_id
                    df=df[~df['fltID'].isin(temp_df.fltID)]
                    final_df=final_df.append(temp_df)
                    i=len(final_df)
                    flag=False
                    temp_df=temp_df[0:0]
                    duty_id+=1
                    
        if( flag == True):
            final_df=final_df.append(g_df)
            df=df[~df['fltID'].isin(g_df.fltID)]
            i=len(final_df)
                
    return final_df              



'''
Fix the empty newDutyId
'''
def fix_dutyNo(all_df):
    all_df = all_df.reset_index(drop=True)  
    duty_id=1
    df=pd.DataFrame()
    ind=0
    all_df['newDutyId']=all_df['newDutyId'].replace('', np.nan)
    for i, g_df in all_df.groupby(all_df.index // 2):
        if pd.isnull(g_df.loc[ind]['newDutyId']):
            g_df.at[ind,'newDutyId']= duty_id
            g_df.at[ind+1,'newDutyId']= duty_id+1
            df=df.append(g_df)
            ind+=2
            duty_id+=2           
        else:
            temp_id=g_df.loc[ind]['newDutyId']
            g_df.at[ind,'newDutyId']= duty_id
            g_df.at[ind+1,'newDutyId']=duty_id
            df=df.append(g_df)
            ind+=2
            if np.not_equal(temp_id, all_df.loc[ind]['newDutyId']):
                duty_id+=1
    return df              
   

'''
This method calculates OrgUTC (duty period begin time) and DestUTC (duty period end time)
Each duty period begin time starts 45 minutes before the flight deprature time. Each duty period
end time ends 45 minutes after flight arrival time
'''
def calculate_duty_period(all_df):
    final_df=pd.DataFrame()
    duty_id=1
    min_45=datetime.timedelta(minutes=+45)
    last_duty_id=all_df.iloc[len(all_df)-1]['newDutyId']
    all_df['OrgUTC'] = pd.to_datetime(all_df['OrgUTC'])
    all_df['DestUTC'] = pd.to_datetime(all_df['DestUTC'])
    all_df['totDutyTm']=''
    while duty_id < last_duty_id :
        df=all_df[all_df['newDutyId'].isin([duty_id])]
        dtyRepTmUTC=df.iloc[0]['OrgUTC']-min_45
        dtyRelTmUTC=df.iloc[len(df)-1]['DestUTC']+min_45
        df['dtyRepTmUTC']=dtyRepTmUTC
        df['dtyRelTmUTC']=dtyRelTmUTC
        df['totDutyTm']=dtyRelTmUTC-dtyRepTmUTC
        duty_id+=1
        final_df=final_df.append(df)
        
    return final_df

#Read B2B flights data

flights_df = pd.read_csv(data_path+"b2b.csv")
flights_df.drop(flights_df.filter(regex="Unname"),axis=1, inplace=True)
final_df=calculate_Duty(flights_df)
final_df.to_csv("combined_duty-b2b.csv")
all_df=final_df

#read B2NB-NB2B data
flights_df = pd.read_csv(data_path+"b2nb_nb2b.csv")
flights_df.drop(flights_df.filter(regex="Unname"),axis=1, inplace=True)
final_df=calculate_Duty(flights_df)
final_df.to_csv("combined_duty-b2nb_nb2b.csv")
all_df=all_df.append(final_df)

all_df=fix_dutyNo(all_df)
all_df=calculate_duty_period(all_df)

all_df.to_csv("combined_duty-b2b-b2nb_nb2b.csv")

    

