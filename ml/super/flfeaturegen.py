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


class FlightFeatureGenerator:
    '''
    This class creates new features for the flights based 
    on following criteria
    1. All flgiths that departs and arrives within a base city 
    is marked as "1" with new feature BASE_FL
    2. All flights with CRS_ELAPSED_TIME <=900 grouped together with
    new feature GROUP=1,2,3, etc.
    '''
    def __init__(self, pairing_month, feature_file, fa_bases, fa_non_bases):
        self.logger = logging.getLogger(__name__)
        self.pairing_month = pairing_month
        self.feature_file = feature_file
        self.fa_bases = fa_bases
        self.fa_non_bases = fa_non_bases
        self.flights_df = pd.read_csv(
            DATA_DIR+self.pairing_month+"/"+self.feature_file)
        self.flights_df.drop(self.flights_df.filter(
            regex="Unname"), axis=1, inplace=True)
        self.flights_df.dropna()
        self.group_id=1

    def process(self):
        self.generate_base_indicator()
        self.generate_pairing_group()

    def generate_base_indicator(self):
        self.flights_df['BASE_FL'] = self.flights_df.apply(
            lambda x: "1" if x['ORIGIN'] and x['DEST'] in self.fa_bases else '0', axis=1)

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
                if total_elapsed_time <= 900:
                    continue
                else:  
                    self.flights_df.loc[(self.flights_df.FL_ID.isin(fl_ids)),'GROUP']=self.group_id
                    total_elapsed_time = 0
                    with pd.option_context('display.max_rows', None, 'display.max_columns', None):
                        print(self.flights_df.loc[self.flights_df.FL_ID.isin(fl_ids)])
                    fl_ids.clear()
                    self.group_id += 1
                    

        nb2nb = [x for x in origin_dest if x[0]
                 in self.fa_non_bases and x[1] in self.fa_non_bases]
        nb2nb = list(set(nb2nb))

        b2nb = [x for x in origin_dest if x[0]
                in self.fa_bases and x[1] in self.fa_non_bases]
        b2nb = list(set(b2nb))

        nb2b = [x for x in origin_dest if x[0]
                in self.fa_non_bases and x[1] in self.fa_bases]
        nb2b = list(set(nb2b))
        self.flights_df = self.flights_df.sort_values('DISTANCE')

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
