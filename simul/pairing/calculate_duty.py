
import pandas as pd
import os.path
import numpy as np
import datetime

data_path=os.path.dirname(__file__)+'/'



'''
Fix the empty newDutyId
'''
def fix_dutyNo(all_df):
    all_df = all_df.reset_index(drop=True)  
    duty_id=1
    df=pd.DataFrame()
    ind=0
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


flights_df = pd.read_csv(data_path+"combined_duty-b2b-b2nb_nb2b.csv")
flights_df.drop(flights_df.filter(regex="Unname"),axis=1, inplace=True)


flights_df=fix_dutyNo(flights_df)
flights_df=calculate_duty_period(flights_df)

flights_df.to_csv("all_duty.csv")