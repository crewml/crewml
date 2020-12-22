import pandas as pd
import os.path
from os import listdir
from os.path import isfile, join
import numpy as np


data_path=os.path.dirname(__file__)+'/'

flights_df=pd.DataFrame()

#,"CVG","SLC","LAX","MCO","BOS","NYC","MSP","SEA","DTW","MIA","FLL","SFO","HNL"
fa_bases=["HNL"]
flights_df = pd.read_csv(data_path+"flights_2020_jan_dl-Copy.csv")

dest_def=pd.DataFrame()
for i in fa_bases:
    origin_df=flights_df[flights_df.Origin == i]
    flights_df=pd.concat([flights_df, origin_df]).drop_duplicates(keep=False)
    origin_df.reset_index(inplace = True, drop = True)
    for column in origin_df[['Dest']]:
        temp=origin_df[column]
        for j in temp:
            temp=flights_df[(flights_df.Origin == j) & (flights_df.Dest == i) ]
            dest_def=dest_def.append(temp, ignore_index = True) 
        

columns=["FltDt","TlNo","FltNo","Org","Dest","DepTm","ArrTm", "DtyRepTm", "DtyRelTm"]

df= pd.DataFrame(columns=columns)

