import pandas as pd
import os.path
import datetime



data_path=os.path.dirname(__file__)+'/'


#combined_df = pd.read_csv(data_path+"combined_duty-b2nb_nb2b.csv")
combined_df = pd.read_csv(data_path+"combined_duty-b2b.csv")
#combined_df=combined_df.head(91)

j=1
final_df=pd.DataFrame()
combined_df["pairID"]=""
toggle=True
hour_8=datetime.timedelta(hours=+8)
temp1=""
combined_df['OrgUTC'] = pd.to_datetime(combined_df['OrgUTC'])
combined_df["DestUTC"] = pd.to_datetime(combined_df['DestUTC'])


def create_pairing(df1, df2,pair_id1,pair_id2):
    df=pd.DataFrame()
    incriment=1
    more=False
    if df1.iloc[0].DestUTC -  df1.iloc[0].OrgUTC >  hour_8  or len(df2)==0:
        df1["pairID"]=pair_id1
        df2["pairID"]=pair_id2
        df=df.append(df1)
        df=df.append(df2)
        incriment=2        
    else:
        d1_time=df1.iloc[0].DestUTC -  df1.iloc[0].OrgUTC
        d2_time=df2.iloc[0].DestUTC -  df2.iloc[0].OrgUTC
        df=df.append(df1)
        df=df.append(df2)
        df["pairID"]=pair_id1
        
        if d1_time+d2_time < hour_8:
            more=True
  
    return df, incriment, more


pair_id=1 
combined_df_len=len(combined_df)
i=1
while (len(final_df) < combined_df_len):
    print("pair_id=",pair_id)
    print("len(final_df)=",len(final_df))
    print("i=",i)
    df1= combined_df[(combined_df.dutyId == i)]
    df2= combined_df[(combined_df.dutyId == i+1)]
     
    df, incriment, more=create_pairing(df1,df2,pair_id,pair_id+1)
    if(more == True):
        i+=2
        df2= combined_df[(combined_df.dutyId == i+1)]
        df, incriment, more=create_pairing(df,df2,pair_id,pair_id+1)
        i+=1
        final_df=final_df.append(df)
    else:   
        final_df=final_df.append(df)
        pair_id+=incriment
        i+=2
        
final_df.to_csv("flights_pairing-b2b.csv")     
   

    


