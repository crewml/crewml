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
import numpy as np

from crewml.config import config
import crewml.common as st
from crewml.exception import CrewmlDataError



class Feature:
    '''
     This class encapsulates DataFrame with features
    '''

    def __init__(self, feature_name="flight", load_dir=None, file_name=None):
        '''
        Create Feature object for the passed-in feature_name. First it checks
        if the feature file already exist. If it doesn't exist

        Parameters
        ----------
        feature_name : str, optional
            DESCRIPTION. The default is "flight". It can be pairing
        load_dir : str, optional
            DESCRIPTION. The default is None.
        file_name : str, optional
            DESCRIPTION. The default is None.

        Raises
        ------
        CrewmlDataError
            DESCRIPTION.

        Returns
        -------
        None.

        '''
        self.logger = logging.getLogger(__name__)
        self.con = config.ConfigHolder(st.RESOURCE_DIR+"pairing_config.ini")
        self.feature_name = feature_name
        self.df = pd.DataFrame()
        self.flight_features = self.con.getValue("flight_features")
        self.flight_features = self.flight_features.split(",")
        # preferred_airline_code has the marketing airline code to load
        # specific airlines
        self.preferred_airline_code = self.con.getValue(
            "preferred_airline_code")
        # if not passed use the default download_dir from the config file
        if load_dir is None:
            self.load_dir = st.ROOT_DIR+self.con.getValue("download_dir")
        else:
            self.load_dir = load_dir

        # if file_name is not passed, check if the system already has the
        # *.csv file, if it finds it, use the latest file from the list. If
        # file_name is passed use that file. At the end of this step either
        # it uses the existing file or passed-in file to load.
        if file_name is None:
            files = os.listdir(self.load_dir)
            files = list(filter(lambda x: x.find(".csv") != -1, files))
            paths = [os.path.join(self.load_dir, basename)
                     for basename in files]
            self.file_name = max(paths, key=os.path.getctime)

        else:
            self.file_name = file_name

        if self.file_name is None:
            raise CrewmlDataError("No file exist in "+load_dir)

    def load(self):
        '''
        Load the file with MKT_UNIQUE_CARRIER equal to MKT_UNIQUE_CARRIER from
        pairing_config.ini file.

        Returns
        -------
        DataFrame
            DataFrame with loaded data from the csv file.

        '''
        self.df = pd.read_csv(self.file_name, usecols=self.flight_features)
        self.df = self.df[self.df.MKT_UNIQUE_CARRIER ==
                          self.preferred_airline_code]
        self.df = self.df.reset_index(drop=True)
        return self.df

    def numeric_feature_names(self):
        '''
        Get the numeric feature names of the loaded data specified in
        pairing_config.ini file

        Returns
        -------
        List
            List of numeric feature names from config file

        '''

        return self.con.getValue("flight_numeric_features").split(",")

    def categorical_feature_names(self):
        '''
        Get the categorial feature names of the loaded data specified in
        pairing_config.ini file

        Returns
        -------
        List
            List of categorial feature names from config file

        '''
        return self.con.getValue("flight_categorical_features").split(",")

    def date_feature_names(self):
        '''
        Get the date feature names of the loaded data specified in
        pairing_config.ini file

        Returns
        -------
        List
            List of date feature names from config file

        '''
        return self.con.getValue("flight_date_features").split(",")

    def all_feature_names(self):
        return list(self.df)

    def all_features(self):
        '''
        Retrun the loaded DataFrame with all the features

        Returns
        -------
        DataFrame
            DESCRIPTION.

        '''
        if self.df.empty:
            self.load()

        return self.df

    def numeric_features(self):
        '''
        Return the numeric features only. It repalces empty values with "0"
        and converts all columns to int

        Returns
        -------
        DataFrame
            DESCRIPTION.

        '''
        feat = self.con.getValue("flight_numeric_features")
        feat = feat.split(",")

        df = self.df[feat]

        # replace empty values with '0' and convert all columns to int
        df = df.replace(np.nan, '0', regex=True)
        df = df.astype(int)

        return df

    def numeric_cat_features(self):
        df1 = self.numeric_features()
        df2 = self.categorical_features()
        df = pd.concat([df1, df2], axis=1)

        return df

    def date_cat_numeric_features(self):
        df1 = self.numeric_features()
        df2 = self.categorical_features()
        df3 = self.date_features()
        df3 = pd.to_datetime(df3).dt.strftime("%Y%m%d")
        df = pd.concat([df3, df2, df1], axis=1)

        return df

    def categorical_features(self):
        '''
        Return Categorical features only

        Returns
        -------
        TYPE
            DESCRIPTION.

        '''
        return self.df[self.con.getValue("flight_categorical_features")
                       .split(",")]

    def date_features(self):
        '''
        Return Date features only

        Returns
        -------
        TYPE
            DESCRIPTION.

        '''
        return self.df[self.con.getValue("flight_date_features")]

    def get_numeric_x_y(self):
        '''
        Return all the unique pairs of numeric features as per the config file

        Returns
        -------
        num_x_y : List
            List contains pair of numerical features

        '''
        num_list = self.con.get_value("flight_plot", "num_dist").split(",")
        num_x_y = list(itertools.combinations(num_list, 2))

        return num_x_y

    def get_category_x_y_z(self):
        '''
        Return all the unique 3-typle of category features
        as per the config file

        Returns
        -------
        num_x_y : List
            List contains pair of numerical features

        '''
        cat_list = self.con.get_value("flight_plot", "cat_dist").split(",")
        cat_x_y_z = list(itertools.combinations(cat_list, 3))

        return cat_x_y_z

    def get_cat_x_y(self):
        '''
        Return all the unique pairs of categorical features as per the
        config file

        Returns
        -------
        num_x_y : List
            List contains pair of numerical features

        '''
        num_list = self.con.get_value("flight_plot", "cat_dist").split(",")
        num_x_y = list(itertools.combinations(num_list, 2))

        return num_x_y

    def get_num_cat_x_y_z(self):
        cat1 = self.categorical_feature_names()
        cat2 = self.categorical_feature_names()
        num = self.numeric_feature_names()
        feat = [num, cat1, cat2]
        coms = list(itertools.product(*feat))
        num_cat_x_y_z = []

        for i in range(len(coms)):
            if coms[i][0] == coms[i][1] or coms[i][1] == coms[i][2] \
                    or coms[i][0] == coms[i][2]:
                continue
            else:
                num_cat_x_y_z.append(coms[i])

        return num_cat_x_y_z

    def get_num_num_cat(self):
        cat = self.categorical_feature_names()
        num1 = self.numeric_feature_names()
        num2 = self.numeric_feature_names()
        feat = [num1, num2, cat]
        coms = list(itertools.product(*feat))
        num_num_cat = []

        for i in range(len(coms)):
            if coms[i][0] == coms[i][1] or coms[i][1] == coms[i][2] \
                    or coms[i][0] == coms[i][2]:
                continue
            else:
                num_num_cat.append(coms[i])

        return num_num_cat

    def get_date_num_cat_x_y_z(self):
        cat = self.categorical_feature_names()
        dt = self.date_feature_names()
        num = self.numeric_feature_names()
        feat = [dt, num, cat]
        coms = list(itertools.product(*feat))
        date_num_cat_x_y_z = []

        for i in range(len(coms)):
            if coms[i][0] == coms[i][1] or coms[i][1] == coms[i][2] \
                    or coms[i][0] == coms[i][2]:
                continue
            else:
                date_num_cat_x_y_z.append(coms[i])

        return date_num_cat_x_y_z

    def get_feature_name(self):
        '''
        Get name of the loaded reature

        Returns
        -------
        TYPE
            DESCRIPTION.

        '''

        return self.feature_name

    def get_max_plots(self):
        return int(self.con.getValue(self.feature_name+"_max_plots"))
