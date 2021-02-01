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
import logging
import pandas as pd
import os

from crewml.config import config
import crewml.common as st
from crewml.exception import CrewmlDataError

class GenericFeature:
    '''
    '''
    
    def __init__(self,feature_name="flight", load_dir=None, file_name=None):
        self.logger = logging.getLogger(__name__)
        self.con=config.ConfigHolder(st.RESOURCE_DIR+"pairing_config.ini")
        self.feature_name=feature_name
        self.df=None
        self.flight_features=self.con.getValue("flight_features")
        self.flight_features=self.flight_features.split(",")
        self.preferred_airline_code=self.con.getValue("preferred_airline_code")
        if load_dir == None :
            self.load_dir=st.ROOT_DIR+self.con.getValue("download_dir")
        else:
            self.load_dir=load_dir
        
        if file_name==None :    
            files = os.listdir(self.load_dir)
            files = list(filter(lambda x: x.find(".csv") !=-1, files))
            paths = [os.path.join(self.load_dir, basename) for basename in files]
            self.file_name=max(paths, key=os.path.getctime)

        else:
            self.file_name=file_name
        
        if self.file_name ==None:
            raise CrewmlDataError("No file exist in "+load_dir)
        
        
    def load(self):       
        self.df = pd.read_csv(self.file_name, usecols=self.flight_features)
        self.df = self.df[self.df.MKT_UNIQUE_CARRIER == self.preferred_airline_code]
        self.df = self.df.reset_index(drop=True)
        return self.df
        
        
    
    def features(self):
        return self.df
    
'''    
gf=GenericFeature()    
flight_df=gf.load()
flight_df.to_csv("flights.csv")
'''
import seaborn as sns

flight_df=pd.read_csv("flights.csv")
flight_df['FL_DATE']=pd.to_datetime(flight_df['FL_DATE'])
flight_df=flight_df.sample(100)
nan_val=flight_df.isnull().values.any()
flight_df=flight_df.fillna(0)
flight_df = flight_df.loc[:, ~flight_df.columns.str.contains('^Unnamed')]
sns.set(style="whitegrid", font_scale=0.5)
#sns.set_theme(style="darkgrid", font_scale=0.1,palette="deep")
sns.set_context("paper")
'''
For sns.displot
sns.displot(data=flight_df, x="ORIGIN")
kind="kde" needs the x feature must be date/numeric
rug=True needs x feature must be Numeric

Currently, bivariate plots (x and y) are available only for histograms and KDEs:
'''
#sns.displot(data=flight_df, x="DISTANCE", hue="DEST",  kind="kde")
#sns.displot(data=flight_df, x="DISTANCE", hue="DEST",   multiple="stack")
#sns.displot(data=flight_df, x="DISTANCE", col="DEST", aspect=.7, multiple="stack")
#sns.relplot(data=flight_df, x="DISTANCE", y="TAIL_NUM", row="DEST", hue="ORIGIN", col="AIR_TIME") #hangs
#sns.relplot(data=flight_df, kind="line") #only numeric/date
#sns.scatterplot(data=flight_df, x="FL_DATE", y="DISTANCE", style="DEST", hue="CRS_DEP_TIME")
#sns.lineplot(data=flight_df, x="FL_DATE", y="DISTANCE", style="DEST", hue="CRS_DEP_TIME") good one
'''
sns.lineplot(
    data=flight_df, x="FL_DATE", y="DISTANCE",
    hue="ORIGIN")  confulsing lines
'''
sns.lineplot(
    data=flight_df, x="FL_DATE", y="DISTANCE", hue="DEST", style="ORIGIN",
)