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


import itertools
import datetime
from crewml.common import DATA_DIR
import logging
import traceback


class FlightCategorizer:
    '''
    List of Delta Flight Attantant (FA) bases. Generally base is set
    of a city which may have more than one airport
    in it. E.g. NYC base has  JFK and LGA airports

    0 2020_feb_classify_b2b.csv,
    1 2020_feb_classify_b2b_missing.csv,
    2 2020_feb_classify_ b2nb_nb2b.csv,
    3 2020_feb_classify_b2nb_nb2b_missing.csv,
    4 2020_feb_classify_nb2nb.csv
    '''

    def __init__(self, fa_bases, fa_non_bases, clean_output, classify_files):
        self.logger = logging.getLogger(__name__)
        self.fa_bases = fa_bases.split(",")
        self.fa_non_bases = fa_non_bases
        self.clean_output = clean_output
        self.classify_files = classify_files
        self.flights_df = None

    def process(self):
        try:
            # Read flights data
            self.flights_df = pd.read_csv(DATA_DIR+self.clean_output)
            self.logger.info("flight data read from:", self.clean_output)

            del self.flights_df['CRS_DEP_TIME']
            del self.flights_df['CRS_ARR_TIME']
            del self.flights_df['ORIGIN_TZ']
            del self.flights_df['DEST_TZ']
            del self.flights_df['MKT_UNIQUE_CARRIER']

            origin_dest = list(
                zip(self.flights_df.ORIGIN, self.flights_df.DEST))

            # use set to remove duplicate flight pairs
            b2b = [x for x in origin_dest if x[0]
                   in self.fa_bases and x[1] in self.fa_bases]
            b2b = list(set(b2b))

            nb2nb = [x for x in origin_dest if x[0]
                     in self.fa_non_bases and x[1] in self.fa_non_bases]
            nb2nb = list(set(nb2nb))

            b2nb = [x for x in origin_dest if x[0]
                    in self.fa_bases and x[1] in self.fa_non_bases]
            b2nb = list(set(b2nb))

            nb2b = [x for x in origin_dest if x[0]
                    in self.fa_non_bases and x[1] in self.fa_bases]
            nb2b = list(set(nb2b))

            # departure from nonbase to arrival nonbase flights
            nb2nb_df = self.group_flights(nb2nb)
            nb2nb_df.to_csv(DATA_DIR+self.classify_files[4])
            self.logger.info("len of nb2nb_df=", len(nb2nb_df))

            # departure base to arrival base flight pairs
            b2b_df = self.group_flights(b2b)
            b2b_fl_pair_df, df1 = self.assemble_B2B_flights(b2b_df)
            b2b_fl_pair_df = self.calculateDuty(b2b_fl_pair_df)
            b2b_fl_pair_df.to_csv(DATA_DIR+self.classify_files[0])
            df1.to_csv(DATA_DIR+self.classify_files[1])

            self.logger.info("b2b Total=", len(b2b_df))
            self.logger.info("len of file %s:%s",
                             self.classify_files[0], len(b2b_fl_pair_df))
            self.logger.info("len of file %s:%s",
                             self.classify_files[1], len(df1))
            self.logger.info("difference between %s and %s=%s",
                             self.classify_files[0], self.classify_files[1],
                             len(b2b_df) -
                             (len(df1)+len(b2b_fl_pair_df)))

            # departure base to arrival non-base flight
            b2nb_df = self.group_flights(b2nb)
            # departure non-base to arrival base flight
            nb2b_df = self.group_flights(nb2b)
            b2nb_nb2b_pair_df, df2 = self.assemble_B2NB_NB2B_flights(
                b2nb_df, nb2b_df)

            b2nb_nb2b_pair_df = self.calculateDuty(b2nb_nb2b_pair_df)
            # df=self.calculateDuty(df2)
            b2nb_nb2b_pair_df.to_csv(DATA_DIR+self.classify_files[2])
            df2.to_csv(DATA_DIR+self.classify_files[3])
            self.logger.info("len of %s=%s", self.classify_files[2],
                             len(b2nb_nb2b_pair_df))
            self.logger.info("len of %s=%s", self.classify_files[3],
                             len(df2))

            self.logger.info("total=", len(
                b2b_fl_pair_df)+len(df1)+len(nb2nb_df) +
                len(b2nb_nb2b_pair_df)+len(df2))
        except Exception as e:
            self.logger.error(traceback.format_exc())
            raise

    '''
    The fl_pairs contain all combinations of tuple like ('CVG', 'MSP'),
    ('EWR', 'DTW'), etc for B2B flights. Similiarly it will have for
    NB2NB flights. This method extract B2B, B2NB, NB2B, NB2NB flights from the
    flight list based on fl_pairs
    '''

    def group_flights(self, fl_pairs):
        df = pd.DataFrame()
        for index, tuple in enumerate(fl_pairs):
            org_airport = tuple[0]
            dest_airport = tuple[1]
            df = df.append(self.flights_df[(self.flights_df['ORIGIN'].isin(
                [org_airport])) & (self.flights_df['DEST'].isin([dest_airport]))])

        df.drop(df.filter(regex="Unname"), axis=1, inplace=True)
        df = df.sort_values('ORIGIN_UTC')
        df.reset_index(drop=True, inplace=True)

        return df

    '''
    This method creates fligh pairs that departs from a base airport
    and arrives to a base airport. The
    pairs will be combined to create a Duty. b2b_df contains all B2B flights

    '''

    def assemble_B2B_flights(self, b2b_df):
        b2b_df['ORIGIN_UTC'] = pd.to_datetime(b2b_df['ORIGIN_UTC'])
        b2b_df["DEST_UTC"] = pd.to_datetime(b2b_df['DEST_UTC'])

        finished_pair = []
        aiport_pair = list(itertools.permutations(self.fa_bases, 2))
        final_df = pd.DataFrame()
        missing_df = pd.DataFrame()
        for index, tuple in enumerate(aiport_pair):
            org_airport = tuple[0]
            dest_airport = tuple[1]

            if (org_airport, dest_airport) in finished_pair:
                continue
            org_df = b2b_df[(b2b_df['ORIGIN'].isin([org_airport])) & (
                b2b_df['DEST'].isin([dest_airport]))]
            org_df.drop(org_df.filter(regex="Unname"), axis=1, inplace=True)
            org_df = org_df.sort_values('ORIGIN_UTC')
            org_df.reset_index(drop=True, inplace=True)

            dest_df = b2b_df[(b2b_df['ORIGIN'].isin([dest_airport])) & (
                b2b_df['DEST'].isin([org_airport]))]
            dest_df = dest_df.drop(dest_df.filter(regex="Unname"), axis=1)
            dest_df = dest_df.sort_values('ORIGIN_UTC')
            dest_df.reset_index(drop=True, inplace=True)

            if (len(org_df) != 0) and (len(dest_df) != 0):
                # org_df contains all same origin flights like ATL and
                # dest_df contains all same dest flights
                # like MSP. assemble_B2NB_NB2B_flights function find the
                # best flight to match the org and dest
                d1, d2 = self.assemble_B2NB_NB2B_flights(org_df, dest_df)
                final_df = final_df.append(d1)
                missing_df = missing_df.append(d2)
            else:
                missing_df = missing_df.append(org_df)
                missing_df = missing_df.append(dest_df)

            finished_pair.append((dest_airport, org_airport))

        # final_df contains flight pairs that starts and ends in same base
        # missing_df contains flight thta starts in a base couldn't be paired
        return final_df, missing_df

    '''
    This method creates flight pairs for B2NB and NB2B.These two
    pairs will be combined to create a Duty.
    B2NB - Flights departs from Base airport and arrives to non base airport
    NB2B - Flights dpearts from non base airport and arrives to base airport
    '''

    def assemble_B2NB_NB2B_flights(self, df1, df2):

        total = len(df1)+len(df2)
        print("toal entering df1=", len(df1),
              "len(df2)=", len(df2), "total=", total)
        final_duty_df = pd.DataFrame()
        missing_df = pd.DataFrame()

        df1['ORIGIN_UTC'] = pd.to_datetime(df1['ORIGIN_UTC'])
        df1["DEST_UTC"] = pd.to_datetime(df1['DEST_UTC'])
        df2['ORIGIN_UTC'] = pd.to_datetime(df2['ORIGIN_UTC'])
        df2["DEST_UTC"] = pd.to_datetime(df2['DEST_UTC'])

        df1 = df1.sort_values('ORIGIN_UTC')
        df2 = df2.sort_values('ORIGIN_UTC')

        for index, first_fl_pair in df1.iterrows():
            print("len of final_duty_df=", len(final_duty_df))
            org_airport = first_fl_pair["ORIGIN"]
            dest_airport = first_fl_pair["DEST"]
            # Collect all the matching fligh pairs for the second pair
            matching_fl_pairs = df2[(df2.ORIGIN == dest_airport)
                       & (df2.DEST == org_airport)]
            total = len(matching_fl_pairs)
            matching_fl_pairs.reset_index(drop=True, inplace=True)
            
            # for each one of first_fl_pair loop through matching_fl_pairs
            # to find a matching matching flight pair if second pair flgiht
            # ORIGIN_UTC > first_fl_pair DEST_UTC+40 min

            i = 0
            temp1 = ""
            while(i < total):
                if matching_fl_pairs.iloc[i].ORIGIN_UTC > first_fl_pair['DEST_UTC'] + \
                        datetime.timedelta(minutes=+45):
                    temp1 = matching_fl_pairs.iloc[i]
                    break
                else:
                    i += 1
                    continue

            if(len(temp1) > 0):
                del_id = temp1.FL_ID
                final_duty_df = final_duty_df.append(first_fl_pair)
                final_duty_df = final_duty_df.append(temp1)
                df2 = df2[df2.FL_ID != del_id]
            else:
                missing_df = missing_df.append(first_fl_pair)

        missing_df = missing_df.append(df2)

        return final_duty_df, missing_df

    '''
    Duty Report time starts 45 minutes before flight departure time
    Duty Release time starts 45 minuts after flight arrival time
    '''

    def calculateDuty(self, df):

        if(len(df) == 0):
            return

        df['DUTY_REP_TM_UTC'] = ''
        df['DUTY_REL_TM_UTC'] = ''

        dtyRepTmUTC = []
        dtyRelTmUTC = []
        df['ORIGIN_UTC'] = pd.to_datetime(df['ORIGIN_UTC'])
        df["DEST_UTC"] = pd.to_datetime(df['DEST_UTC'])

        first = True
        for orgUTC, destUTC in zip(df.ORIGIN_UTC, df.DEST_UTC):
            if first:
                temp1 = orgUTC+datetime.timedelta(minutes=-45)
                dtyRepTmUTC.append(temp1)
                first = False
            else:
                dtyRepTmUTC.append(temp1)
                dtyRelTmUTC.append(destUTC+datetime.timedelta(minutes=+45))
                dtyRelTmUTC.append(destUTC+datetime.timedelta(minutes=+45))
                first = True

        if len(dtyRepTmUTC) != len(dtyRelTmUTC):
            dtyRepTmUTC.pop()
            dtyRepTmUTC.append("")
            dtyRelTmUTC.append("")

        df["DUTY_REP_TM_UTC"] = dtyRepTmUTC
        df["DUTY_REL_TM_UTC"] = dtyRelTmUTC

        df.reset_index(drop=True, inplace=True)

        return df

        # return calculate_dutyNo(df)

    '''
    If the total duty time (dtyRepTmUTC-dtyRelTmUTC) for the flight
    pair is greater than 6 hours
    then those two flights in the pair will get seperate dutyId.
    If not it will get same dutyId
    '''

    def calculate_dutyNo(self, df):
        df.reset_index(drop=True, inplace=True)
        df['DTY_REP_TM_UTC'] = pd.to_datetime(df['DTY_REP_TM_UTC'], utc=True)
        df['DTY_REL_TM_UTC'] = pd.to_datetime(df['DTY_REL_TM_UTC'], utc=True)
        ind = 0
        duty_id = 1
        hours_6 = datetime.timedelta(hours=+6)
        all_df = pd.DataFrame()

        for i, g_df in df.groupby(df.index // 2):
            if g_df.loc[ind]['DTY_REL_TM_UTC'] - g_df.loc[ind]['DTY_REP_TM_UTC'] > \
                    hours_6:
                g_df.at[ind, 'DUTY_ID'] = duty_id
                g_df.at[ind+1, 'DUTY_ID'] = duty_id+1
                duty_id += 2
            else:
                g_df['DUTY_ID'] = duty_id
                duty_id += 1

            all_df = all_df.append(g_df)
            ind += 2
            print("all_df=", len(all_df), "time=", datetime.datetime.now())

        return all_df
