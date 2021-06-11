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
import logging
import pickle
from crewml.common import DEPLOY_DIR
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report
from sklearn.metrics import accuracy_score
from sklearn.metrics import matthews_corrcoef
from sklearn.metrics import balanced_accuracy_score
import joblib

class PairingModelDeployer:
    def __init__(self,
                 model_file,
                 flight_file):
        self.logger = logging.getLogger(__name__)
        self.model_file = model_file
        self.flight_file = flight_file
        with open(DEPLOY_DIR+self.model_file, 'rb') as file:
            self.pairing_model = joblib.load(file)

        self.flights_df = pd.read_csv(
            DEPLOY_DIR+self.flight_file)
        self.flights_df.drop(self.flights_df.filter(
            regex="Unname"), axis=1, inplace=True)
        

    def predict_pairings(self):
        
        pair_freq = self.select_pairings(400)
        self.flights_df = self.flights_df.loc[self.flights_df['PAIRING_ID']
                                              .isin(pair_freq['index1'])]



        self.encode_pairing_target()
        self.flights_df = self.flights_df.drop(['PAIRING_ID'], axis=1)
        predictions = self.pairing_model.predict(self.flights_df)

        #predictions_df = pd.DataFrame({'PREDICTIONS': predictions[:, 0]})

        print("XGBoost Test Classification Report")
        print(classification_report(self.target_df, predictions))

        accuracy = accuracy_score(self.target_df, predictions)
        print("Accuracy: %.2f%%" % (accuracy * 100.0))

        matt_score = matthews_corrcoef(self.target_df, predictions)
        print("matthews_corrcoef=%s" % matt_score)

        balanced_score = balanced_accuracy_score(
            self.target_df, predictions)
        print("balanced_accuracy_score=%s" % balanced_score)

    def encode_pairing_target(self):
        '''
        Use label encoder to encode the target pairing Ids to start from
        0, 1, 2, ... XGBoost requires target to start from 0 instead of
        random PAIRING_IDs selected from select_pairings() function.


        Returns
        -------
        None.

        '''       
        self.target_df = self.flights_df['PAIRING_ID']
        le = LabelEncoder()
        le.fit(self.target_df)

        encoded = le.transform(self.target_df)
        self.target_df = pd.DataFrame(encoded, columns=['PAIRING_ID'])
        self.original_target_df = le.inverse_transform(self.target_df)

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
        pair_freq = self.flights_df['PAIRING_ID'].value_counts(dropna=False)
        pair_freq.index = pair_freq.index.map(int)
        pair_freq = pair_freq[:total]
        pair_freq = pair_freq.to_frame()
        pair_freq['index1'] = pair_freq.index
        
        return pair_freq