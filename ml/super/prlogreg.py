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
from category_encoders import TargetEncoder
import numpy as np
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
from sklearn import ensemble
from sklearn.metrics import classification_report, confusion_matrix
import xgboost as xgb
from sklearn.model_selection import cross_val_score
from sklearn.metrics import accuracy_score
import logging
from crewml.common import DATA_DIR
from sklearn.metrics import matthews_corrcoef
from sklearn.metrics import balanced_accuracy_score
import crewml.common as st
import pickle
from sklearn import preprocessing
from sklearn.model_selection import RandomizedSearchCV, GridSearchCV
import joblib


class PairingLogRegressor:
    def __init__(self, feature_file,
                 pairing_month,
                 pairing_model_output_file,
                 paring_model_file):
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
        self.pairing_month = pairing_month
        self.pairing_model_output_file = pairing_model_output_file
        self.paring_model_file = paring_model_file

    def process(self):
        '''
        Prepars Pairing data for Logistic Regression

        Returns
        -------
        None.

        '''
        self.pairing_df = pd.read_csv(
            DATA_DIR+self.pairing_month+"/"+self.feature_file)
        self.pairing_df.drop(self.pairing_df.filter(
            regex="Unname"), axis=1, inplace=True)
        self.clean_pairing()

        pair_freq = self.select_pairings(400)
        self.pairing_df = self.pairing_df.loc[self.pairing_df['PAIRING_ID']
                                              .isin(pair_freq['index1'])]

        # convert timedetal to seconds
        self.pairing_df['AIR_TIME'] = pd.to_timedelta(
            self.pairing_df['AIR_TIME']).dt.seconds
        self.pairing_df['TOT_DUTY_TM'] = pd.to_timedelta(
            self.pairing_df['TOT_DUTY_TM']).dt.seconds
        self.pairing_df['TOT_PAIRING_UTC'] = pd.to_timedelta(
            self.pairing_df['TOT_PAIRING_UTC']).dt.seconds

        self.remove_duty_columns()

        self.target_df = pd.DataFrame()
        self.target_df['PAIRING_ID'] = self.pairing_df['PAIRING_ID']
        self.encode_pairing_target()

        # copy the selected features to save it to output file
        self.selected_pairing_df = self.pairing_df.copy()
        self.selected_pairing_df.to_csv(
            DATA_DIR+self.pairing_month+"/"+self.pairing_model_output_file)

        del self.pairing_df['PAIRING_ID']

    def get_selected_pairings(self):
        '''
        Return subset of Pairings used to train the model. Only the flight IDs
        returned in this model is used in Model deployment to identify the
        PAIRING_IDs for new month
        '''
        return self.selected_pairing_df

    def select_pairings(self, total):
        '''
        This function selects total pairings to be given to the model.
        Instead of passing all the pairings, we can select "total" number of
        pairings to train and test the model. There are many pairing exist
        with only two flights in it and it is not enough to train a pairing
        category just with two flights. Until we can get more data by
        combining multiple months or improving our pairing generation
        algorithm to incude more flights for a given pairing, this function
        will choose top "total" pairings which has more flights in it.

        Returns
        -------
        pair_freq : pairing frequencey

        '''
        pair_freq = self.pairing_df['PAIRING_ID'].value_counts(dropna=False)
        pair_freq.index = pair_freq.index.map(int)
        pair_freq = pair_freq[:total]
        pair_freq = pair_freq.to_frame()
        pair_freq['index1'] = pair_freq.index

        return pair_freq

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
        '''
        indices_to_keep = ~self.pairing_df.isin(
            [np.nan, np.inf, -np.inf]).any(1)

        self.pairing_df[indices_to_keep].astype(np.float64)
        '''

    def encode_pairing_target(self):
        '''
        Use label encoder to encode the target pairing Ids to start from
        0, 1, 2, ... XGBoost requires target to start from 0 instead of
        random PAIRING_IDs selected from select_pairings() function.


        Returns
        -------
        None.

        '''

        le = preprocessing.LabelEncoder()
        le.fit(self.target_df)

        encoded = le.transform(self.target_df)
        self.target_df = pd.DataFrame(encoded, columns=['PAIRING_ID'])
        self.original_target_df = le.inverse_transform(self.target_df)

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
                self.pairing_df, self.target_df,
                test_size=0.30, random_state=40)

    def xgboost_classifier(self):
        '''
        Using the train and test data crete XGBClassifier
        to train and test the Pairing data

        Returns
        -------
        None.

        '''
        xgb_model = xgb.XGBClassifier(
            booster="gbtree",
            # error evaluation for multiclass training
            objective="multi:softmax",
            n_gpus=0,
            n_jobs=-1,
            gamma=1,
            max_depth=4,
            learning_rate=0.01,
            # use_label_encoder=False,
            n_estimators=1000,
            num_class=len(self.target_df.PAIRING_ID.unique()),
            eval_metric="mlogloss",
            verbosity=1,
            min_child_weight=1
            # reg_alpha=reg_alpha,
            # max_depth=max_depth,
            # subsample=subsample,
            # colsample_bytree= colsample_bytree,
            # min_child_weight= min_child_weight,
            # params
        )
        print("total num_classes=", len(self.target_df.PAIRING_ID.unique()))

        # self.perform_coross_validation(xgb_model)

        xgb_model.fit(self.X_train, self.y_train)
        xgboost_predictions = xgb_model.predict(self.X_test)
        print("XGBoost Test  Confusion Matrix:")
        print(confusion_matrix(self.y_test, xgboost_predictions))

        print("XGBoost Test Classification Report")
        print(classification_report(self.y_test, xgboost_predictions))

        accuracy = accuracy_score(self.y_test, xgboost_predictions)
        print("Accuracy: %.2f%%" % (accuracy * 100.0))

        matt_score = matthews_corrcoef(self.y_test, xgboost_predictions)
        print("matthews_corrcoef=%s" % matt_score)

        balanced_score = balanced_accuracy_score(
            self.y_test, xgboost_predictions)
        print("balanced_accuracy_score=%s" % balanced_score)

        # dump model with feature map
        pickle.dump(xgb_model, open(DATA_DIR+self.pairing_month +
                                    "/"+self.paring_model_file, "wb"))

    def remove_duty_columns(self):
        '''
        Remove features that are used in creating the pairings but will
        not available in the flights feature, when the flights are passed
        to the trained model to identify the pairing classification.

        Returns
        -------
        None.

        '''
        self.pairing_df = self.pairing_df.drop(['DUTY_REP_TM_UTC',
                                                'DUTY_REL_TM_UTC',
                                                'NEW_DUTY_ID',
                                                'TOT_DUTY_TM',
                                                'TOT_PAIRING_UTC',
                                                'FL_KEY',
                                                'TAIL_NUM',
                                                'FL_ID',
                                                'LAYOVER'], axis=1)

    def xgboost_model_parms(self):
        params = {
            "learning_rate": [0.05, 0.10, 0.15, 0.20, 0.25, 0.30],
            "max_depth": [3, 4, 5, 6, 8, 10, 12, 15],
            "min_child_weight": [1, 3, 5, 7],
            "gamma": [0.0, 0.1, 0.2, 0.3, 0.4],
            "colsample_bytree": [0.3, 0.4, 0.5, 0.7],
            "objective": ["multi:softprob", "multi:softmax"]

        }
        classifier = xgb.XGBClassifier(use_label_encoder=False)
        random_search = RandomizedSearchCV(classifier,
                                           param_distributions=params,
                                           n_iter=5,
                                           scoring='accuracy',
                                           n_jobs=-1,
                                           cv=5,
                                           verbose=1)
        self.encode_pairing()
        random_search.fit(self.pairing_df,
                          self.target_df)

        print(random_search.best_estimator_)
        classifier = random_search.best_estimator_
        scores = cross_val_score(classifier,
                                 self.pairing_df,
                                 self.target_df)
        print("Cross validation %0.2f accuracy with a standard \
              deviation of %0.2f" %
              (scores.mean(), scores.std()))

    def encode_origin_dest(self):
        '''
        Use TargetEncoder to encode the flight Origin and Destination
        '''
        encoder = TargetEncoder()
        self.pairing_df['Origin'] = encoder.\
            fit_transform(self.pairing_df['Origin'],
                          self.pairing_df['PAIRING_ID'])
        encoder = TargetEncoder()
        self.pairing_df['Dest'] = encoder\
            .fit_transform(self.pairing_df['Dest'],
                           self.pairing_df['PAIRING_ID'])
        encoder = TargetEncoder()
        self.pairing_df['Tail_Number'] = encoder\
            .fit_transform(self.pairing_df['Tail_Number'],
                           self.pairing_df['PAIRING_ID'])

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
        to train and test the Pairing data

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

    def perform_coross_validation(self, xgb_model):
        # find cross validation
        # score XGBClassifier
        f1_micro = cross_val_score(
            xgb_model, self.pairing_df, self.target_df,
            cv=5, scoring='f1_micro')
        f1_macro = cross_val_score(
            xgb_model, self.pairing_df, self.target_df,
            cv=5, scoring='f1_macro')
        f1_weighted = cross_val_score(
            xgb_model, self.pairing_df, self.target_df,
            cv=5, scoring='f1_weighted')
        neg_log_loss = cross_val_score(
            xgb_model, self.pairing_df, self.target_df,
            cv=5, scoring='neg_log_loss')
        # roc not supported for multi class
        # roc_auc = cross_val_score(
        #    xgb_model, self.pairing_df, self.target_df,
        #    cv=5, scoring='roc_auc')

        print("f1_micro %0.2f accuracy with a standard deviation of %0.2f" %
              (f1_micro.mean(), f1_micro.std()))
        print("f1_macro %0.2f accuracy with a standard deviation of %0.2f" %
              (f1_macro.mean(), f1_macro.std()))
        print("f1_weighted %0.2f accuracy with a standard \
              deviation of %0.2f" %
              (f1_weighted.mean(), f1_weighted.std()))
        print("neg_log_loss %0.2f accuracy with a standard \
              deviation of %0.2f" %
              (neg_log_loss.mean(), neg_log_loss.std()))

        scores = cross_val_score(xgb_model, self.pairing_df, self.target_df)
        print("Cross validation %0.2f accuracy with a standard \
              deviation of %0.2f" %
              (scores.mean(), scores.std()))
