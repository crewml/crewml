import pandas as pd
import os.path
from category_encoders import TargetEncoder
import pandas as pd
import numpy as np
from sklearn.metrics import r2_score
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error

from sklearn import ensemble
import matplotlib.pyplot as plt
import _pickle as cPickle


#Use XGBoost forest alg
params = {'n_estimators': 200,
          'max_depth': 30,
          'min_samples_split': 5
          }
model_xgboost_for = ensemble.RandomForestRegressor(**params)

with open('xgboost_random_forest.pkl', "rb") as f:
    model = cPickle.load(f)
    
    
data_path=os.path.dirname(__file__)+'/'

flights_df = pd.read_csv("C:\\Mani\\ML\\flights\\dev\\flight_pairing.csv")
flights_df.drop(flights_df.filter(regex="Unname"),axis=1, inplace=True)
#convert timedetal to seconds
flights_df['FltTime']=pd.to_timedelta(flights_df['FltTime']).dt.seconds
flights_df['totDutyTm']=pd.to_timedelta(flights_df['totDutyTm']).dt.seconds
flights_df['totPairingUTC']=pd.to_timedelta(flights_df['totPairingUTC']).dt.seconds

#convert datetime into second
flights_df['OrgUTC']=pd.to_datetime(flights_df['OrgUTC'])
flights_df['OrgUTC']=flights_df.OrgUTC.astype(int)

flights_df['DestUTC']=pd.to_datetime(flights_df['DestUTC'])
flights_df['DestUTC']=flights_df.OrgUTC.astype(int)

flights_df['dtyRelTmUTC']=pd.to_datetime(flights_df['dtyRelTmUTC'])
flights_df['dtyRelTmUTC']=flights_df.dtyRelTmUTC.astype(int)

flights_df['dtyRepTmUTC']=pd.to_datetime(flights_df['dtyRepTmUTC'])
flights_df['dtyRepTmUTC']=flights_df.OrgUTC.astype(int)

#Convert flight date to int
flights_df['FlightDate']=flights_df.FlightDate.str.replace("/","").astype(int)


#flights_df.groupby('Origin').boxplot(fontsize=15,rot=50,figsize=(20,20),patch_artist=True)

temp1=flights_df[flights_df['pairingId'].isnull()]
temp1['pairingId']=0
temp2=flights_df[~flights_df['fltID'].isin(temp1.fltID)]
temp2['pairingId']=1
flights_df=temp1.append(temp2)

'''
Use TargetEncoder to encode the flight Origin and Destination

encoder = TargetEncoder()
flights_df['Origin'] = encoder.fit_transform(flights_df['Origin'], flights_df['cost'])
encoder = TargetEncoder()
flights_df['Dest'] = encoder.fit_transform(flights_df['Dest'], flights_df['cost'])
encoder = TargetEncoder()
flights_df['Tail_Number'] = encoder.fit_transform(flights_df['Tail_Number'], flights_df['cost'])
'''

del flights_df['Origin']
del flights_df['Dest']
del flights_df['Tail_Number']
del flights_df['pairingId']


'''
Clean the data for Nan and too large values
'''
def clean_dataset(df):
    assert isinstance(df, pd.DataFrame), "df needs to be a pd.DataFrame"
    df.dropna(inplace=True)
    indices_to_keep = ~df.isin([np.nan, np.inf, -np.inf]).any(1)
    return df[indices_to_keep].astype(np.float64)

clean_dataset(flights_df)
model_predict = model.predict(flights_df)

with open('model_predict.txt', 'w') as f:
    for item in model_predict:
        f.write("%s\n" % item)





