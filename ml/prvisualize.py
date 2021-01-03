
import pandas as pd
import os.path
import numpy as np
import matplotlib.pyplot as plt
from category_encoders import TargetEncoder
import seaborn as sns
from sklearn.feature_selection import f_regression, mutual_info_regression
from scipy import stats
from setup import DATA_DIR
import logging
import os.path







'''
temp1=flights_df[flights_df['pairingId'].isnull()]
temp1['pairingId']=0
temp2=flights_df[~flights_df['fltID'].isin(temp1.fltID)]
temp2['pairingId']=1
flights_df=temp1.append(temp2)

Use TargetEncoder to encode the flight Origin and Destination

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

class PairingVisualizer:
    def __init__(self, feature_file):
        self.logger = logging.getLogger(__name__)
        self.feature_file=feature_file
        self.pairing_df=None
        
        print("feature_file=",feature_file)
    
    def process(self):
        self.pairing_df = pd.read_csv(DATA_DIR+self.feature_file)
        self.logger.info("Pairing data read from:", self.feature_file)
        
        self.pairing_df.drop(self.pairing_df.filter(regex="Unname"),axis=1, inplace=True)
                
        #convert time to seconds
        self.pairing_df['FltTime']=pd.to_timedelta(self.pairing_df['FltTime']).dt.seconds
        self.pairing_df['totDutyTm']=pd.to_timedelta(self.pairing_df['totDutyTm']).dt.seconds
        self.pairing_df['totPairingUTC']=pd.to_timedelta(self.pairing_df['totPairingUTC']).dt.seconds
        
        #convert datetime into second
        self.pairing_df['OrgUTC']=pd.to_datetime(self.pairing_df['OrgUTC'])
        self.pairing_df['OrgUTC']=self.pairing_df.OrgUTC.astype(int)
        
        self.pairing_df['DestUTC']=pd.to_datetime(self.pairing_df['DestUTC'])
        self.pairing_df['DestUTC']=self.pairing_df.OrgUTC.astype(int)
        
        self.pairing_df['dtyRelTmUTC']=pd.to_datetime(self.pairing_df['dtyRelTmUTC'])
        self.pairing_df['dtyRelTmUTC']=self.pairing_df.dtyRelTmUTC.astype(int)
        
        self.pairing_df['dtyRepTmUTC']=pd.to_datetime(self.pairing_df['dtyRepTmUTC'])
        self.pairing_df['dtyRepTmUTC']=self.pairing_df.OrgUTC.astype(int)


        #Convert flight date to int
        self.pairing_df['FlightDate']=self.pairing_df.FlightDate.str.replace("/","").astype(int)
        
    def create_box_plot(self):
        self.pairing_df.groupby('Origin').boxplot(fontsize=15,rot=50,figsize=(30,30),patch_artist=True)
