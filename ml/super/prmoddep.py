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
from crewml.common import MODEL_DIR


class PairingModelDeployer:
    def __init__(self, model_file):
        self.logger = logging.getLogger(__name__)
        self.model_file = model_file
        self.pairing_model = pd.read_pickle(MODEL_DIR+self.model_file)

    def predict_pairings(self, flights):
        self.flights_df = flights
        self.transform_flights()
        predictions = self.pairing_model.predict(flights)
        print(predictions)

    def transform_flights(self):
        # convert datetime into second
        self.flights_df['ORIGIN_UTC'] = pd.to_datetime(
            self.flights_df['ORIGIN_UTC'])

        self.flights_df['ORIGIN_DAY'] = self.flights_df['ORIGIN_UTC'].dt.day
        self.flights_df['ORIGIN_MONTH'] = self.flights_df['ORIGIN_UTC'].dt.month
        self.flights_df['ORIGIN_YEAR'] = self.flights_df['ORIGIN_UTC'].dt.year
        self.flights_df['ORIGIN_HOUR'] = self.flights_df['ORIGIN_UTC'].dt.hour
        self.flights_df['ORIGIN_MINUTE'] = self.flights_df['ORIGIN_UTC'].dt.minute

        self.flights_df['DEST_UTC'] = pd.to_datetime(
            self.flights_df['DEST_UTC'])
        self.flights_df['DEST_DAY'] = self.flights_df['DEST_UTC'].dt.day
        self.flights_df['DEST_MONTH'] = self.flights_df['DEST_UTC'].dt.month
        self.flights_df['DEST_YEAR'] = self.flights_df['DEST_UTC'].dt.year
        self.flights_df['DEST_HOUR'] = self.flights_df['DEST_UTC'].dt.hour
        self.flights_df['DEST_MINUTE'] = self.flights_df['DEST_UTC'].dt.minute
        self.flights_df = self.flights_df.drop(['ORIGIN_UTC',
                                                'DEST_UTC'], axis=1)

        self.flights_df['FL_DATE'] = pd.to_datetime(
            self.flights_df['FL_DATE'])
        self.flights_df['FL_DATE_DAY'] = self.flights_df['FL_DATE'].dt.day
        self.flights_df['FL_DATE_MONTH'] = self.flights_df['FL_DATE'].dt.month
        self.flights_df['FL_DATE_YEAR'] = self.flights_df['FL_DATE'].dt.year

        self.flights_df = self.flights_df.drop(['FL_DATE'], axis=1)


