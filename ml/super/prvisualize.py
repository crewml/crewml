'''
__author__=Mani Malarvannan

MIT License

Copyright (c) 2020 crewml

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''

import pandas as pd
import os.path
import numpy as np
import matplotlib.pyplot as plt
from category_encoders import TargetEncoder
import seaborn as sns
from sklearn.feature_selection import f_regression, mutual_info_regression
from scipy import stats
from common import DATA_DIR
import logging





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
        self.pairing_df['FlightDate'] = self.pairing_df['FlightDate'].astype(str)
        
        self.pairing_df['FlightDate']=self.pairing_df.FlightDate.str.replace("-","").astype(int)
    
    '''
    Create box plot for the pairing data retrieved and processed from the process
    function
    '''
    def plot_box(self):
        self.pairing_df.groupby('Origin').boxplot(fontsize=15,rot=50,figsize=(30,30),patch_artist=True)
        plt.show()
    '''
    Use the TargetEncoder to encode Origin, Dest, TailNumber features, these 
    feature has alphanumeric and this function converts it to numeric using
    TargetEncoder
    '''
    def encode_pairing_feature(self):
        temp1=self.pairing_df[self.pairing_df['pairingId'].isnull()]
        temp1['pairingId']=0
        temp2=self.pairing_df[~self.pairing_df['fltID'].isin(temp1.fltID)]
        temp2['pairingId']=1
        self.pairing_df=temp1.append(temp2)
        
        #Use TargetEncoder to encode the flight Origin and Destination 
        encoder = TargetEncoder()
        self.pairing_df['Origin'] = encoder.fit_transform(self.pairing_df['Origin'], self.pairing_df['cost'])
        encoder = TargetEncoder()
        self.pairing_df['Dest'] = encoder.fit_transform(self.pairing_df['Dest'], self.pairing_df['cost'])
        encoder = TargetEncoder()
        self.pairing_df['Tail_Number'] = encoder.fit_transform(self.pairing_df['Tail_Number'], self.pairing_df['cost'])
        
        #print column name with total nan values in it
        nan_col_count=self.pairing_df.isna().sum()
        logging.info("Number of NA values for each feature")
        logging.info(nan_col_count)
    
    '''
    Plot histogram graph for the pairing feature
    '''    
    def plot_histogram(self):
        self.pairing_df['cost'].plot.hist(title="Flight Cost Distribution")
        plt.xlabel('Cost')
        plt.ylabel('# of occurance')
        plt.show()
        
    '''
    Default it uses Pearson corralation coefficient that goes from -1 to 1  
    '''        
    def calculate_Correlations(self):
        correlations = self.pairing_df.corr()
        plt.figure(figsize=(12,10))
        sns.heatmap(correlations, annot=True, cmap=plt.cm.Reds)
        correlations = correlations['cost']
        logging.info(correlations)
   
    '''
    plot passed-in feature with the target "cost" to visualize the corralation     
    '''    
    def plot_scatter(self, feature):
        #plot each feature with the target "cost" to visualize the corralation 
        self.pairing_df.plot.scatter(x=feature, y='cost')
        plt.show()
        
    
    '''
    plot pivot for the passed-in feature with the 
    '''
    def plot_pivot(self, feature):
        #Pivot plot shows the relationship between two features or a feature/target
        pivot = pd.pivot_table(self.pairing_df.sample(10), values='cost', index=[feature], aggfunc=np.mean)
        pivot.plot(kind='bar')
        plt.show()
        

    '''
    pairplot gives histogram of all the numerical features along the diagonal and shows the 
    graph between two features
    '''    
    def plot_pair(self, feature):
        sns.set_style("whitegrid");
        #sns.pairplot(abs(self.pairing_df.sample(1000)),size=3)
        sns.pairplot(self.pairing_df.sample(1000), hue=feature, size=3)
        sns.boxplot(x=feature,y='cost',data=self.pairing_df.sample(10))
        plt.show()

    def plot_join_plot(self, feature, target):
        j = sns.jointplot(feature, target, data = self.pairing_df, kind = 'reg')
        j.annotate(stats.pearsonr)
        plt.show()


        
        
        
    