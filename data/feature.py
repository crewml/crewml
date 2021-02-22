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
import itertools

from crewml.config import config
import crewml.common as st
from crewml.exception import CrewmlDataError

class Feature:
    '''
    '''
    
    def __init__(self,feature_name="flight", load_dir=None, file_name=None):
        self.logger = logging.getLogger(__name__)
        self.con=config.ConfigHolder(st.RESOURCE_DIR+"pairing_config.ini")
        self.feature_name=feature_name
        self.df=pd.DataFrame()
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
        
    def numeric_feature_names(self):
       return self.con.getValue("flight_numeric_features").split(",")

    def categorical_feature_names(self):
       return self.con.getValue("flight_categorical_features").split(",")

    def date_feature_names(self):
       return self.con.getValue("flight_date_features").split(",")
    
    def all_features(self):
        if self.df.empty:
            self.load()
            
        return self.df
    
    def numeric_features(self):
       feat=self.con.getValue("flight_numeric_features")
       feat=feat.split(",")
       return self.df[feat]

    def categorical_features(self):
       return self.df[self.con.getValue("flight_categorical_features")]

    def date_features(self):
       return self.df[self.con.getValue("flight_date_features")]
   
    def get_numeric_x_y(self):
        num_list=self.con.get_value("flight_plot","num_dist").split(",")
        num_x_y=list(itertools.combinations(num_list,2))
        
        return num_x_y
        
    def get_feature_name(self):
       return self.feature_name
    
   
