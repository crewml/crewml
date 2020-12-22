
import pandas as pd
import os.path
from category_encoders import TargetEncoder
import pandas as pd
import numpy as np
from sklearn import model_selection
from sklearn.linear_model import LinearRegression
from sklearn.linear_model import Ridge
from sklearn.linear_model import Lasso
from sklearn.linear_model import ElasticNet
from sklearn.neighbors import KNeighborsRegressor
from sklearn.tree import DecisionTreeClassifier
from sklearn.svm import SVR
from sklearn.metrics import r2_score
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
from math import sqrt
from sklearn import ensemble
import matplotlib.pyplot as plt
import _pickle as cPickle
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.metrics import f1_score


data_path=os.path.dirname(__file__)+'/'

flights_df = pd.read_csv(data_path+"all_feb_flights_with_cost.csv")

flights_df=flights_df.sample(100)
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

'''
temp1=flights_df[flights_df['pairingId'].isnull()]
temp1['pairingId']=0
temp2=flights_df[~flights_df['fltID'].isin(temp1.fltID)]
temp2['pairingId']=1
flights_df=temp1.append(temp2)
'''

'''
Use TargetEncoder to encode the flight Origin and Destination
'''
encoder = TargetEncoder()
flights_df['Origin'] = encoder.fit_transform(flights_df['Origin'], flights_df['pairingId'])
encoder = TargetEncoder()
flights_df['Dest'] = encoder.fit_transform(flights_df['Dest'], flights_df['pairingId'])
encoder = TargetEncoder()
flights_df['Tail_Number'] = encoder.fit_transform(flights_df['Tail_Number'], flights_df['pairingId'])



'''
Clean the data for Nan and too large values
'''
def clean_dataset(df):
    assert isinstance(df, pd.DataFrame), "df needs to be a pd.DataFrame"
    df.dropna(inplace=True)
    indices_to_keep = ~df.isin([np.nan, np.inf, -np.inf]).any(1)
    return df[indices_to_keep].astype(np.float64)

clean_dataset(flights_df)
flights_df['pairingId'] = 'P' + flights_df['pairingId'].astype(str)

target_df=pd.DataFrame()
target_df['pairingId']=flights_df['pairingId']
del flights_df['pairingId']



#Split data into train and test
X_train, X_test, y_train, y_test = train_test_split(flights_df, target_df, test_size=0.30, random_state=40)

#----------use DecisionTree to fit the data------------
dtree = DecisionTreeClassifier(max_depth=25, min_samples_leaf=0.13, random_state=3)
dtree.fit(X_train, y_train)

pred_train_tree_classify= dtree.predict(X_train)
print(" DecisionTree Train Confusion Matrix:")
print(confusion_matrix(y_train, pred_train_tree_classify))

print(" DecisionTree Train Classification Report")
print(classification_report(y_train, pred_train_tree_classify))



pred_test_tree_classify= dtree.predict(X_test)
print(" DecisionTree Train Confusion Matrix:")
print(confusion_matrix(y_test, pred_test_tree_classify))

print(" DecisionTree Train Classification Report")
print(classification_report(y_test, pred_test_tree_classify))



#Use XGBoost regresstion alg
params = {'n_estimators': 500,
          'max_depth': 4,
          'min_samples_split': 5,
          'learning_rate': 0.01}
model_xgboost_classify = ensemble.GradientBoostingClassifier(**params)
model_xgboost_classify.fit(X_train, y_train)
pred_train_xg_classify= model_xgboost_classify.predict(X_train)
print("GradientBoosting Train Confusion Matrix:")
print(confusion_matrix(y_train, pred_train_xg_classify))

print("GradientBoosting Train Classification Report")
print(classification_report(y_train, pred_train_xg_classify))

pred_test_xg_classify = model_xgboost_classify.predict(X_test)
print("GradientBoosting Test Confusion Matrix:")
print(confusion_matrix(y_test, pred_test_xg_classify))

print("GradientBoosting Test Classification Report")
print(classification_report(y_test, pred_test_xg_classify))

#-----------------------------------------------------
#Use XGBoost forest alg
params = {'n_estimators': 200,
          'max_depth': 30,
          'min_samples_split': 5
          }
model_xgboost_for = ensemble.RandomForestClassifier(**params)
model_xgboost_for.fit(X_train, y_train)
pred_train_xg_for= model_xgboost_for.predict(X_train)
print("RandomForest Train Confusion Matrix:")
print(confusion_matrix(y_train, pred_train_xg_for))

print("RandomForest Train Classification Report")
print(classification_report(y_train, pred_train_xg_for))

pred_test_xg_for = model_xgboost_for.predict(X_test)
print("RandomForest Test  Confusion Matrix:")
print(confusion_matrix(y_test, pred_test_xg_for))

print("RandomForest Test Classification Report")
print(classification_report(y_test, pred_test_xg_for))

#Store the model for future use
'''
with open('xgboost_random_forest.pkl', 'wb') as fid:
    cPickle.dump(model_xgboost_for, fid)    
'''