import itertools
import pandas as pd
import os.path
import numpy as np
import matplotlib.pyplot as plt
from category_encoders import TargetEncoder
import seaborn as sns
from sklearn.feature_selection import f_regression, mutual_info_regression
from scipy import stats

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


flights_df.groupby('Origin').boxplot(fontsize=15,rot=50,figsize=(20,20),patch_artist=True)

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


flights_df['cost'].plot.hist(title="Flight Cost Distribution")
plt.xlabel('Cost')
plt.ylabel('# of occurance')

print("Correlations") 
#Default it uses Pearson corralation coefficient that goes from -1 to 1           
correlations = flights_df.corr()
plt.figure(figsize=(12,10))
sns.heatmap(correlations, annot=True, cmap=plt.cm.Reds)
correlations = correlations['cost']
print(correlations)

#plot each feature with the target "cost" to visualize the corralation 
flights_df.plot.scatter(x='Dest', y='cost')


#Pivot plot shows the relationship between two features or a feature/target
pivot = pd.pivot_table(flights_df.sample(10), values='cost', index=['totPairingUTC'], aggfunc=np.mean)
pivot.plot(kind='bar')

#pairplot gives histogram of all the numerical features along the diagonal and shows the 
#graph between two features
sns.set_style("whitegrid");
#sns.pairplot(abs(flights_df.sample(1000)),size=3)
#sns.pairplot(flights_df.sample(1000), hue="Origin", size=3);

#sns.boxplot(x='Origin',y='cost',data=flights_df.sample(10))

def plot_join_plot(df, feature, target):
    j = sns.jointplot(feature, target, data = df, kind = 'reg')
    j.annotate(stats.pearsonr)
    return plt.show()

plot_join_plot(flights_df, "Dest", "cost")

'''
feature selection methods
Filter methods
    chi square
    Anova Test
    Corralation coefficient
Wrapper Methods
    Forward selection
    Backward selection
    Recursive feature elemination
Embeeded Method

Mutual Selection (non-linear models)

'''


