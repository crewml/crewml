
import pandas as pd
import os.path
import numpy as np
import matplotlib.pyplot as plt
from category_encoders import TargetEncoder

from sklearn.feature_selection import SelectKBest
from sklearn.feature_selection import chi2
from sklearn.feature_selection import f_classif
from sklearn.feature_selection import VarianceThreshold
from sklearn.feature_selection import f_regression, mutual_info_regression
from sklearn.model_selection import train_test_split

data_path=os.path.dirname(__file__)+'/'

flights_df = pd.read_csv(data_path+"all_flights_with_cost.csv")
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
'''
encoder = TargetEncoder()
flights_df['Origin'] = encoder.fit_transform(flights_df['Origin'], flights_df['cost'])
encoder = TargetEncoder()
flights_df['Dest'] = encoder.fit_transform(flights_df['Dest'], flights_df['cost'])
encoder = TargetEncoder()
flights_df['Tail_Number'] = encoder.fit_transform(flights_df['Tail_Number'], flights_df['cost'])

#print column name with total nan values in it
nan_col_count=flights_df.isna().sum()
print("Number of NA values for each feature")
print(nan_col_count)

def clean_dataset(df):
    assert isinstance(df, pd.DataFrame), "df needs to be a pd.DataFrame"
    df.dropna(inplace=True)
    indices_to_keep = ~df.isin([np.nan, np.inf, -np.inf]).any(1)
    return df[indices_to_keep].astype(np.float64)

print("Correlations")           
correlations = flights_df.corr()
correlations = correlations['cost']
print(correlations)

flights_df=clean_dataset(flights_df)
target_df=pd.DataFrame()
target_df['target']=flights_df['cost']
del flights_df['cost']
flights_df = flights_df.reset_index()
del flights_df['index']

#Use VarianceThreshold to eliminate features with low variance
sel = VarianceThreshold(threshold=(.8 * (1 - .8)))
conv=sel.fit_transform(flights_df)
print(conv)

#mi = mutual_info_regression(flights_df, target_df, random_state=0)

#flights_df_new = SelectKBest(chi2, k=10).fit_transform(flights_df,target_df)
flights_df_new = SelectKBest(f_regression, k=10).fit_transform(flights_df, target_df)



'''
feature selection methods
Filter methods (Univariate selection)
    chi square
    Anova Test
    Corralation coefficient
Wrapper Methods
    Forward selection
    Backward selection
    Recursive feature elemination
Embeeded Method

'''
'''
f_regression is used for features that are linearly related

f_test, _ = f_regression(flights_df, target_df)
f_test /= np.max(f_test)

mutual_info_regression is used for non-linear features

mi = mutual_info_regression(flights_df, target_df)
'''
X_train, X_test, y_train, y_test = train_test_split(flights_df, target_df, test_size=0.33, random_state=42)
flights_df_new = SelectKBest(f_regression, k=10).fit_transform(X_train, y_train)

