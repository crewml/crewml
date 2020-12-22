import pandas as pd
import os.path

import itertools
import datetime
import numpy as np

data_path=os.path.dirname(__file__)+'/'

'''
List of Delta Flight Attantant (FA) bases. Generally base is set of a city which may have more than one airport
in it. E.g. NYC base has  JFK and LGA airports
'''
fa_bases=["ATL","HNL","CVG","SLC","LAX","MCO","BOS","EWR","JFK","LGA","MSP","SEA","DTW","MIA","FLL","SFO","PBI","SNA"]

#List of airports that are not in FA base city
fa_non_bases=["ERI","EWN","SGF","MEM","BWI","SHV","DEN","DAB","PNS","FSD","IAD","FAY","SAV","LEX","BNA","OAK"
,"AVP","GEG","MOB","OAJ","OKC","AGS","ORH","STL","DAL","GSO","ONT","ASE","SJU","BIL","AZO","DFW","GRR","SJC"
,"DSM","FNT","IAH","FCA","GTR","PIA","MLU","MLI","BTM","JAC","APN","CLE","OGG","HDN","CHO","MGM","LGB","ABY"
,"COS","CHS","SAN","MHT","ESC","CIU","GPT","TLH","STX","GJT","BTR","MDT","TRI","PDX","MKE","XNA","TWF","PLN"
,"VPS","CLT","SDF","CRW","BOI","PHL","GRB","LNK","DAY","ROA","RDM","MOT","IDA","MSY","ORF","RIC","FAI"
,"LAN","FWA","RST","SCE","BHM","MSN","LAS","MTJ","KOA","ELP","BTV","SBN","GFK","RSW","SAT","IND","VLD","CPR"
,"DCA","PWM","TUL","BIS","LIH","PHX","CHA","BGM","MQT","PIT","SUN","BDL","BUF","XWA","IMT","CAK","SGU","MYR"
,"PSC","BGR","STT","OMA","ANC","ICT","RAP","EVV","MFR","MCI","CMH","DHN","LSE","EGE","ROC","BMI","BZN","GSP"
,"CID","ABE","MSO","TPA","MLB","TYS","FAT","SBA","HHH","FAR","ECP","PHF","PVD","INL","LWS","BJI","HRL","ILM"
,"RNO","SRQ","ORD","EYW","LIT","BUR","AVL","AEX","GNV","CWA","HPN","LFT","EUG","RDU","MDW","GTF","CAE","RHI"
,"PSP","SYR","DLH","BRD","ABQ","JAN","PIH","JAX","ATW","TVC","HIB","ABR","SMF","MBS","FSM","EKO","CSG","AUS"
,"ALB","ELM","CDC","TUS","HSV","ITH","SWF","BQK","HLN", "HOU"]






def create_Flight_Pairs(fl_pairs):
    df=pd.DataFrame()
    for index, tuple in enumerate(fl_pairs):
        org_airport = tuple[0]
        dest_airport = tuple[1]
        df=df.append(flights_df[(flights_df['Origin'].isin([org_airport])) &  (flights_df['Dest'].isin([dest_airport]))] )   
    
    df.drop(df.filter(regex="Unname"),axis=1, inplace=True)
    df=df.sort_values('OrgUTC')
    df.reset_index(drop=True,inplace=True)   
    
    return df



'''
This method creates flight pairs for B2NB and NB2B.These two pairs will be combined to 
create a Duty.
B2NB - Flights departs from Base airport and arrives to non base airport
NB2B - Floghts dpearts from non base airport and arrives to base airport 

'''
def assemble_4_flights(df1, df2, df3, df4):
    final_df=pd.DataFrame()
    missing_df=pd.DataFrame()

    df1['OrgUTC'] = pd.to_datetime(df1['OrgUTC'])
    df1["DestUTC"] = pd.to_datetime(df1['DestUTC'])
    df2['OrgUTC'] = pd.to_datetime(df2['OrgUTC'])
    df2["DestUTC"] = pd.to_datetime(df2['DestUTC'])
    df3['OrgUTC'] = pd.to_datetime(df3['OrgUTC'])
    df3["DestUTC"] = pd.to_datetime(df3['DestUTC'])
    df4['OrgUTC'] = pd.to_datetime(df4['OrgUTC'])
    df4["DestUTC"] = pd.to_datetime(df4['DestUTC'])

    
    df1=df1.sort_values('OrgUTC')
    df2=df2.sort_values('OrgUTC')
    df3=df3.sort_values('OrgUTC')
    df4=df4.sort_values('OrgUTC')
    
    for index, row in df1.iterrows():
        flight1=check_origin_flight_match(row, df2)
        if(len(flight1)!=0):
            flight2=check_origin_flight_match(flight1, df3)   
            if(len(flight2)!=0):
                flight3=check_flight_match(row,flight2,df4) 
                
        if len(flight1)!=0 and len(flight2)!=0 and len(flight3):
          final_df=final_df.append(row)
          final_df=final_df.append(flight1)
          final_df=final_df.append(flight2)
          final_df=final_df.append(flight3)
          df2 = df2[df2.fltID != flight1.fltID]
          df3 = df3[df3.fltID != flight2.fltID]
          df4 = df4[df4.fltID != flight3.fltID]
          print("len(final_df)=",len(final_df))
        else:
          missing_df=missing_df.append(row)
          print("len(missing_df)=",len(missing_df))
          
    missing_df=missing_df.append(df2)
    missing_df=missing_df.append(df3)
    missing_df=missing_df.append(df4)        
  
    return final_df, missing_df

def assemble_3_flights(df1, df2, df3):
    final_df=pd.DataFrame()
    missing_df=pd.DataFrame()

    df1['OrgUTC'] = pd.to_datetime(df1['OrgUTC'])
    df1["DestUTC"] = pd.to_datetime(df1['DestUTC'])
    df2['OrgUTC'] = pd.to_datetime(df2['OrgUTC'])
    df2["DestUTC"] = pd.to_datetime(df2['DestUTC'])
    df3['OrgUTC'] = pd.to_datetime(df3['OrgUTC'])
    df3["DestUTC"] = pd.to_datetime(df3['DestUTC'])
    
    df1=df1.sort_values('OrgUTC')
    df2=df2.sort_values('OrgUTC')
    df3=df3.sort_values('OrgUTC')
    
    for index, row in df1.iterrows():
        flight1=check_origin_flight_match(row, df2)
        if(len(flight1)!=0):
            flight2=check_flight_match(row,flight1, df3)    
               
        if len(flight1)!=0 and len(flight2)!=0 :
          final_df=final_df.append(row)
          final_df=final_df.append(flight1)
          final_df=final_df.append(flight2)
          df2 = df2[df2.fltID != flight1.fltID]
          df3 = df3[df3.fltID != flight2.fltID]
          print("len(final_df)=",len(final_df))
        else:
          missing_df=missing_df.append(row)
          print("len(missing_df)=",len(missing_df))
          
    missing_df=missing_df.append(df2)
    missing_df=missing_df.append(df3)      
  
    return final_df, missing_df



def check_origin_flight_match(flight, df):
    temp=pd.DataFrame()

    temp= df[(df.Origin == flight["Dest"])] 
    for index, row in temp.iterrows():
        if flight.DestUTC+datetime.timedelta(minutes=+45) < row['OrgUTC']:
            return row
    return pd.DataFrame(columns = temp.columns)


def check_flight_match(flight1, flight2, df):
    temp=pd.DataFrame()
    temp= df[(flight1["Origin"] == df.Dest) & (df.Origin == flight2["Dest"]) ]
    for index, row in temp.iterrows():
        if flight2.DestUTC+datetime.timedelta(minutes=+45) < row['OrgUTC']:
            return row
    return pd.DataFrame(columns = temp.columns)
    

'''
Duty Report time starts 45 minutes before flight departure time
Duty Release time starts 45 minuts after flight arrival time
'''        
def calculateDuty(df):
    
    if(len(df) ==0):
        return
    
    df['dtyRepTmUTC']=''
    df['dtyRelTmUTC']=''

    dtyRepTmUTC=[]
    dtyRelTmUTC=[]
    df['OrgUTC'] = pd.to_datetime(df['OrgUTC'])
    df["DestUTC"] = pd.to_datetime(df['DestUTC'])
    

    first=True
    for orgUTC, destUTC in zip(df.OrgUTC,df.DestUTC):  
        if first :
            temp1=orgUTC+datetime.timedelta(minutes=-45)        
            dtyRepTmUTC.append(temp1)
            first=False
        else:   
            dtyRepTmUTC.append(temp1)
            dtyRelTmUTC.append(destUTC+datetime.timedelta(minutes=+45))
            dtyRelTmUTC.append(destUTC+datetime.timedelta(minutes=+45))
            first=True
                   
    if len(dtyRepTmUTC) != len(dtyRelTmUTC):
        dtyRepTmUTC.pop()
        dtyRepTmUTC.append("")
        dtyRelTmUTC.append("")       
                                
    df["dtyRepTmUTC"]=dtyRepTmUTC  
    df["dtyRelTmUTC"]=dtyRelTmUTC  
    

    df.reset_index(drop=True,inplace=True) 
    df['dutyId']= (df.index / 2 + 1).astype(int)
    
        





#Read flights data
#flights_df = pd.read_csv(data_path+"flights_cleaned.csv")
#chosen_idx = np.random.choice(5000, replace=False, size=20)
#flights_df = flights_df.iloc[chosen_idx]

flights1_df = pd.read_csv(data_path+"nb2nb.csv")
flights2_df = pd.read_csv(data_path+"b2b_missing.csv")
flights3_df = pd.read_csv(data_path+"b2nb_nb2b_missing.csv")

flights_miss_df=flights1_df.append(flights2_df)
flights_miss_df=flights_miss_df.append(flights3_df)


flights_miss_df.drop(flights_miss_df.filter(regex="Unname"),axis=1, inplace=True)
flights_miss_df.reset_index(drop=True,inplace=True) 



origin_dest=list(zip(flights_miss_df.Origin, flights_miss_df.Dest))

b2b=[x for x in origin_dest if x[0] in fa_bases and x[1] in fa_bases]
b2b=list(set(b2b))


nb2nb=[x for x in origin_dest if x[0]  in fa_non_bases and  x[1]  in fa_non_bases]
nb2nb=list(set(nb2nb))

b2nb=[x for x in origin_dest if x[0]  in fa_bases and x[1]  in fa_non_bases]
b2nb=list(set(b2nb))

nb2b=[x for x in origin_dest if x[0]  in fa_non_bases and x[1]  in fa_bases]
nb2b=list(set(nb2b))


#departure base to arrival base flight pairs
b2b_df=create_Flight_Pairs(b2b)
b2nb_df= create_Flight_Pairs(b2nb)
nb2nb_df=create_Flight_Pairs(nb2nb)
nb2b_df= create_Flight_Pairs(nb2b)



df1, df2=assemble_3_flights(b2b_df,b2nb_df,nb2b_df)


print("total length=",len(df1)+len(df2))
  

    

