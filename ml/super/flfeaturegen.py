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
from crewml.common import DATA_DIR
from sklearn.preprocessing import LabelEncoder
from category_encoders import TargetEncoder


class FlightFeatureGenerator:
    '''
    This class creates new features for the flights based
    on following criteria
    1. All flgiths that departs and arrives within a base city
    is marked as "1" with new feature BASE_FL
    2. All flights with CRS_ELAPSED_TIME <=900 grouped together with
    new feature GROUP=1,2,3, etc.
    '''

    def __init__(self, pairing_month,
                 feature_file,
                 feature_gen_file,
                 fa_bases,
                 fa_non_bases):
        self.logger = logging.getLogger(__name__)
        self.pairing_month = pairing_month
        self.feature_file = feature_file
        self.fa_bases = fa_bases
        self.fa_non_bases = fa_non_bases
        self.feature_gen_file = feature_gen_file
        self.flights_df = pd.read_csv(
            DATA_DIR+self.pairing_month+"/"+self.feature_file)
        self.flights_df.drop(self.flights_df.filter(
            regex="Unname"), axis=1, inplace=True)
        self.flights_df.dropna()
        self.flights_df['ORIGIN_UTC'] = pd.to_datetime(
            self.flights_df['ORIGIN_UTC'])
        self.flights_df['DEST_UTC'] = pd.to_datetime(
            self.flights_df['DEST_UTC'])
        self.group_id = 1
        self.final_df = pd.DataFrame()

    def process(self):
        self.timestamp2_epoch()
        #self.time2_int()

        # self.generate_base_indicator()
        # self.generate_pairing_group()
        self.label_encode_categories()
        # self.target_encode_categories()
        # self.onehot_encode_categories()
        # self.origin_dest_diff()
        # self.combine_origin_dest()
        self.convert_fl_date()
        self.flights_df.to_csv(
            DATA_DIR+self.pairing_month+"/"+self.feature_gen_file)

    def generate_base_indicator(self):
        self.flights_df['BASE_FL'] = self.flights_df.apply(
            lambda x: "1" if x['ORIGIN'] and x['DEST'] in self.fa_bases else '0', axis=1)

    def origin_dest_diff(self):
        self.flights_df["DEST_ARR_DIFF"] = self.flights_df['DEST_UTC'] - \
            self.flights_df['ORIGIN_UTC']

    def combine_origin_dest(self):
        '''
        Create a new feature=DEST_ARR_DIFF ^ (ORIGIN+DEST)

        Returns
        -------
        None.

        '''
        self.flights_df["ORIGIN"] = self.flights_df["ORIGIN"].astype(int)
        self.flights_df["DEST"] = self.flights_df["DEST"].astype(int)
        temp = self.flights_df["ORIGIN"]+self.flights_df["DEST"]
        self.flights_df["DEST_ARR_DIFF_SQR"] = \
            self.flights_df["DEST_ARR_DIFF"] * (
            self.flights_df["ORIGIN"]-self.flights_df["DEST"])

    def generate_pairing_group(self):
        origin_dest = list(
            zip(self.flights_df.ORIGIN, self.flights_df.DEST))

        # use set to remove duplicates
        b2b = [x for x in origin_dest if x[0]
               in self.fa_bases and x[1] in self.fa_bases]
        b2b = list(set(b2b))

        for i in b2b:
            df = self.group_flights(i)
            if len(df) is None:
                continue

            df = df.sort_values('ORIGIN_UTC')
            total_elapsed_time = 0
            fl_ids = []
            self.flights_df['GROUP'] = ""
            for index, row in df.iterrows():
                total_elapsed_time += row["CRS_ELAPSED_TIME"]
                fl_ids.append(int(row["FL_ID"]))
                if total_elapsed_time <= 900 or len(fl_ids) % 2 == 0:
                    continue
                else:
                    self.flights_df.loc[self.flights_df.FL_ID.isin(fl_ids),
                                        'GROUP'] = str(self.group_id)
                    self.final_df = self.final_df.append(
                        self.flights_df[self.flights_df['FL_ID'].isin(fl_ids)])
                    self.flights_df = \
                        self.flights_df[~self.flights_df.FL_ID.isin(fl_ids)]
                    total_elapsed_time = 0
                    fl_ids.clear()
                    self.group_id += 1

        self.final_df = self.final_df.append(self.flights_df)

        nb2nb = [x for x in origin_dest if x[0]
                 in self.fa_non_bases and x[1] in self.fa_non_bases]
        nb2nb = list(set(nb2nb))

        b2nb = [x for x in origin_dest if x[0]
                in self.fa_bases and x[1] in self.fa_non_bases]
        b2nb = list(set(b2nb))

        nb2b = [x for x in origin_dest if x[0]
                in self.fa_non_bases and x[1] in self.fa_bases]
        nb2b = list(set(nb2b))

        self.flights_df = self.final_df

    '''
    The fl_pairs contain all combinations of tuple like ('CVG', 'MSP'),
    ('EWR', 'DTW'), etc for B2B flights. Similiarly it will have for
    NB2NB flights. This method extract B2B, B2NB, NB2B, NB2NB flights from the
    flight list based on fl_pairs
    '''

    def group_flights(self, fl_pairs):
        df = pd.DataFrame()
        org_airport = fl_pairs[0]
        dest_airport = fl_pairs[1]
        df = df.append(self.flights_df[(self.flights_df['ORIGIN'].isin(
            [org_airport])) &
            (self.flights_df['DEST'].isin([dest_airport]))])

        df.drop(df.filter(regex="Unname"), axis=1, inplace=True)
        df = df.sort_values('ORIGIN_UTC')
        df.reset_index(drop=True, inplace=True)

        return df

    def convert_fl_date(self):
        self.flights_df["FL_DATE"] = pd.to_datetime(
            self.flights_df["FL_DATE"]).dt.strftime("%m%d%Y")

    def time2_int(self):
        # convert datetime into second
        self.flights_df['ORIGIN_UTC'] = self.flights_df.ORIGIN_UTC.astype(
            'int64')//1e9

        self.flights_df['DEST_UTC'] = self.flights_df.DEST_UTC.astype(
            'int64')//1e9

        # Convert flight date to int
        self.flights_df["FL_DATE"] = pd.to_datetime(
            self.flights_df["FL_DATE"]).dt.strftime('%Y/%m/%d')

        self.flights_df['FL_DATE'] = self.flights_df.FL_DATE.str.replace(
            "/", "").astype(int)

    def timestamp2_epoch(self):

        self.flights_df['ORIGIN_UTC'] = self.flights_df['ORIGIN_UTC'].apply(
            lambda x: x.timestamp())
        self.flights_df['DEST_UTC'] = self.flights_df['DEST_UTC'].apply(
            lambda x: x.timestamp())

    def split_timestamp(self):
        '''
        Split the timestamp into individual compoenents
        year, month, day, etc

        Returns
        -------
        None.

        '''

        self.flights_df['ORIGIN_DAY'] = self.flights_df['ORIGIN_UTC'].dt.day
        self.flights_df['ORIGIN_MONTH'] = self.flights_df['ORIGIN_UTC'].dt.month
        self.flights_df['ORIGIN_YEAR'] = self.flights_df['ORIGIN_UTC'].dt.year
        self.flights_df['ORIGIN_HOUR'] = self.flights_df['ORIGIN_UTC'].dt.hour
        self.flights_df['ORIGIN_MINUTE'] = self.flights_df['ORIGIN_UTC'].dt.minute

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

        # Convert flight date to int

    def target_encode_categories(self):
        '''
        Use TargetEncoder to encode the flight Origin and Destination
        '''
        encoder = TargetEncoder()
        self.flights_df['ORIGIN'] = encoder.fit_transform(
            self.flights_df['ORIGIN'], self.flights_df['PAIRING_ID'])
        encoder = TargetEncoder()
        self.flights_df['DEST'] = encoder.fit_transform(
            self.flights_df['DEST'], self.flights_df['PAIRING_ID'])
        encoder = TargetEncoder()
        self.flights_df['TAIL_NUM'] = encoder.fit_transform(
            self.flights_df['TAIL_NUM'], self.flights_df['PAIRING_ID'])

    def label_encode_categories(self):
        encoder = LabelEncoder()
        self.flights_df['ORIGIN'] = encoder.fit_transform(
            self.flights_df['ORIGIN'])
        encoder = LabelEncoder()
        self.flights_df['DEST'] = encoder.fit_transform(
            self.flights_df['DEST'])
        encoder = LabelEncoder()
        self.flights_df['TAIL_NUM'] = encoder.fit_transform(
            self.flights_df['TAIL_NUM'])

    def onehot_encode_categories(self):
        self.flights_df = pd.get_dummies(self.flights_df, prefix=['ORIGIN'],
                                         columns=['ORIGIN'],
                                         drop_first=True)
        self.flights_df = pd.get_dummies(self.flights_df, prefix=['DEST'],
                                         columns=['DEST'],
                                         drop_first=True)
        self.flights_df = pd.get_dummies(self.flights_df, prefix=['TAIL_NUM'],
                                         columns=['TAIL_NUM'],
                                         drop_first=True)
