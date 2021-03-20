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
import logging
from crewml.common import DATA_DIR


class PairingLogRegressor:
    def __init__(self, feature_file):
        '''

        Parameters
        ----------
        feature_file : TYPE
            Name of input file to read pairing data

        Returns
        -------
        None.

        '''
        self.logger = logging.getLogger(__name__)
        self.feature_file = feature_file
        self.pairing_df = None
        self.target_df = None
        self.X_train = None
        self.X_test = None
        self.y_train = None
        self.y_test = None

    def process(self):
        '''
        Prepars Pairing data for Logistic Regression

        Returns
        -------
        None.

        '''
        self.pairing_df = pd.read_csv(DATA_DIR+self.feature_file)
        self.pairing_df.drop(self.pairing_df.filter(
            regex="Unname"), axis=1, inplace=True)
        # convert timedetal to seconds
        self.pairing_df['AIR_TIME'] = pd.to_timedelta(
            self.pairing_df['AIR_TIME']).dt.seconds
        self.pairing_df['TOT_DUTY_TM'] = pd.to_timedelta(
            self.pairing_df['TOT_DUTY_TM']).dt.seconds
        self.pairing_df['TOT_PAIRING_UTC'] = pd.to_timedelta(
            self.pairing_df['TOT_PAIRING_UTC']).dt.seconds

        # convert datetime into second
        self.pairing_df['ORIGIN_UTC'] = pd.to_datetime(
            self.pairing_df['ORIGIN_UTC'])
        self.pairing_df['ORIGIN_UTC'] = self.pairing_df.ORIGIN_UTC.astype(int)

        self.pairing_df['DEST_UTC'] = pd.to_datetime(
            self.pairing_df['DEST_UTC'])
        self.pairing_df['DEST_UTC'] = self.pairing_df.DEST_UTC.astype(int)

        self.pairing_df['DUTY_REL_TM_UTC'] = pd.to_datetime(
            self.pairing_df['DUTY_REL_TM_UTC'])
        self.pairing_df['DUTY_REL_TM_UTC'] = \
            self.pairing_df.DUTY_REL_TM_UTC.astype(
            int)

        self.pairing_df['DUTY_REP_TM_UTC'] = pd.to_datetime(
            self.pairing_df['DUTY_REP_TM_UTC'])
        self.pairing_df['DUTY_REP_TM_UTC'] = \
            self.pairing_df.DUTY_REP_TM_UTC.astype(
            int)

        # Convert flight date to int
        self.pairing_df['FL_DATE'] = self.pairing_df.FL_DATE.str.replace(
            "/", "").astype(int)

        '''
        Use TargetEncoder to encode the flight Origin and Destination
        '''
        encoder = TargetEncoder()
        self.pairing_df['ORIGIN'] = encoder.fit_transform(
            self.pairing_df['ORIGIN'], self.pairing_df['PAIRING_ID'])
        encoder = TargetEncoder()
        self.pairing_df['DEST'] = encoder.fit_transform(
            self.pairing_df['DEST'], self.pairing_df['PAIRING_ID'])
        encoder = TargetEncoder()
        self.pairing_df['TAIL_NUM'] = encoder.fit_transform(
            self.pairing_df['TAIL_NUM'], self.pairing_df['PAIRING_ID'])

        del self.pairing_df['ORIGIN']
        del self.pairing_df['DEST']
        del self.pairing_df['TAIL_NUM']

        pairing_ids = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10']
        self.pairing_df = self.pairing_df.loc[self.pairing_df
                                              ['PAIRING_ID'].isin(pairing_ids)]
        self.remove_duty_columns()
        # self.pairing_df = self.pairing_df.sample(1000)
        # self.clean_pairing()

        # remove rows with empty PAIRING_ID
        # temp1=self.pairing_df[self.pairing_df['PAIRING_ID'].isnull()]
        # self.pairing_df=self.pairing_df-temp1

        print("Null values=", self.pairing_df.isnull().sum())

        self.target_df = pd.DataFrame()
        self.target_df['PAIRING_ID'] = self.pairing_df['PAIRING_ID']
        del self.pairing_df['PAIRING_ID']

    def clean_pairing(self):
        '''
         Clean the data for Nan and too large values

        Returns
        -------
        None.

        '''
        assert isinstance(
            self.pairing_df, pd.DataFrame), "df needs to be a pd.DataFrame"
        self.pairing_df.dropna(inplace=True)
        indices_to_keep = ~self.pairing_df.isin(
            [np.nan, np.inf, -np.inf]).any(1)

        self.pairing_df[indices_to_keep].astype(np.float64)

    def split_feature(self):
        '''
        Splits Pairing feature into test and train data sets
        Returns
        -------
        None.

        '''
        # Split data into train and test
        self.X_train, self.X_test, self.y_train, \
            self.y_test = train_test_split(
                self.pairing_df, self.target_df, test_size=0.30, random_state=40)

    def decision_tree_classifier(self):
        '''
        Using the train and test data crete DecisionTreeClassifier
        to train and test the
        Pairing data

        Returns
        -------
        None.

        '''
        # ----------use DecisionTree to fit the data------------
        dtree = DecisionTreeClassifier(
            max_depth=25, min_samples_leaf=0.13, random_state=3)
        dtree.fit(self.X_train, self.y_train)

        pred_train_tree_classify = dtree.predict(self.X_train)
        print(" DecisionTree Train Confusion Matrix:")
        print(confusion_matrix(self.y_train, pred_train_tree_classify))

        print(" DecisionTree Train Classification Report")
        print(classification_report(self.y_train, pred_train_tree_classify))

        pred_test_tree_classify = dtree.predict(self.X_test)
        print(" DecisionTree Test Confusion Matrix:")
        print(confusion_matrix(self.y_test, pred_test_tree_classify))

        print(" DecisionTree Train Classification Report")
        print(classification_report(self.y_test, pred_test_tree_classify))

    def gradient_boost_classifier(self):
        '''
        Using the train and test data crete GradientBoostingClassifier
        to train and test the
        Pairing data

        Returns
        -------
        None.

        '''
        # Use XGBoost regresstion alg
        params = {'n_estimators': 500,
                  'max_depth': 4,
                  'min_samples_split': 5,
                  'learning_rate': 0.01}
        model_xgboost_classify = ensemble.GradientBoostingClassifier(**params)
        model_xgboost_classify.fit(self.X_train, self.y_train)
        pred_train_xg_classify = model_xgboost_classify.predict(self.X_train)
        print("GradientBoosting Train Confusion Matrix:")
        print(confusion_matrix(self.y_train, pred_train_xg_classify))

        print("GradientBoosting Train Classification Report")
        print(classification_report(self.y_train, pred_train_xg_classify))

        pred_test_xg_classify = model_xgboost_classify.predict(self.X_test)
        print("GradientBoosting Test Confusion Matrix:")
        print(confusion_matrix(self.y_test, pred_test_xg_classify))

        print("GradientBoosting Test Classification Report")
        print(classification_report(self.y_test, pred_test_xg_classify))

    def random_forest_classifier(self):
        '''
        Using the train and test data crete GradientBoostingClassifier
        to train and test the
        Pairing data

        Returns
        -------
        None.

        '''
        # Use XGBoost forest alg
        params = {'n_estimators': 200,
                  'max_depth': 30,
                  'min_samples_split': 5
                  }
        model_xgboost_for = ensemble.RandomForestClassifier(**params)
        model_xgboost_for.fit(self.X_train, self.y_train)
        pred_train_xg_for = model_xgboost_for.predict(self.X_train)
        print("RandomForest Train Confusion Matrix:")
        print(confusion_matrix(self.y_train, pred_train_xg_for))

        print("RandomForest Train Classification Report")
        print(classification_report(self.y_train, pred_train_xg_for))

        pred_test_xg_for = model_xgboost_for.predict(self.X_test)
        print("RandomForest Test  Confusion Matrix:")
        print(confusion_matrix(self.y_test, pred_test_xg_for))

        print("RandomForest Test Classification Report")
        print(classification_report(self.y_test, pred_test_xg_for))

    def remove_duty_columns(self):
        self.pairing_df.drop(['DUTY_REP_TM_UTC',
                              'DUTY_REL_TM_UTC',
                              'NEW_DUTY_ID',
                              'TOT_DUTY_TM',
                              'TOT_PAIRING_UTC',
                              'LAYOVER'], axis=1)
