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
import numpy as np
import datetime
import crewml.common as st
import logging
import traceback

'''
This class takes classified flights and creates duties
'''

#    dutygen_files=2020_feb_classify_b2b.csv,
# 2020_feb_classify_ b2nb_nb2b.csv, 2020_feb_dutygen.csv


class DutyGenerator:
    duty_id = 1

    def __init__(self, files):
        self.logger = logging.getLogger(__name__)
        self.files = files

    def process(self):
        try:
            # Read B2B flights data
            flights_df = pd.read_csv(st.DATA_DIR+self.files[0])
            self.logger.info("B2B flight data read from:", self.files[0])
            flights_df.drop(flights_df.filter(
                regex="Unname"), axis=1, inplace=True)
            final_df = self.calculate_Duty(flights_df)
            all_df = final_df

            # read B2NB-NB2B data
            flights_df = pd.read_csv(st.DATA_DIR+self.files[1])
            self.logger.info("B2NB-NB2B flight data read from:", self.files[1])
            flights_df.drop(flights_df.filter(
                regex="Unname"), axis=1, inplace=True)
            final_df = self.calculate_Duty(flights_df)
            # final_df.to_csv("combined_duty-b2nb_nb2b.csv")
            all_df = all_df.append(final_df)

            all_df = self.fix_dutyNo(all_df)
            all_df = self.calculate_duty_period(all_df)

            all_df.to_csv(st.DATA_DIR+self.files[2])
            self.logger.info("%s file generated with size %s:", \
                             self.files[2],len(all_df))
        except Exception as e:
            self.logger.error(traceback.format_exc())
            raise

    def calculate_Duty(self, df):
        if(len(df) == 0):
            return

        df['ORIGIN_UTC'] = pd.to_datetime(df['ORIGIN_UTC'])
        df["DEST_UTC"] = pd.to_datetime(df['DEST_UTC'])

        final_temp_df = pd.DataFrame()
        df["NEW_DUTY_ID"] = ""

        while(len(df) != 0):
            '''
            Iterate df with two rows at a time, E.g. ATL-HNL and HNL-ATL
            two flights considered as one unit
            '''
            for i, g_df in df.groupby(df.index // 2):
                temp1_df = df.loc[(df["ORIGIN"] == g_df.iloc[0].ORIGIN) & (
                    df["DEST"] == g_df.iloc[0].DEST)]
                temp2_df = df.loc[(df["ORIGIN"] == g_df.iloc[1].ORIGIN) & (
                    df["DEST"] == g_df.iloc[1].DEST)]
                temp_df = temp1_df.append(temp2_df)
                temp_df.sort_index(inplace=True)

                if len(temp_df) != 0:
                    final_temp_df = final_temp_df.append(
                        self.chunk_flights(temp_df))
                    df = df[~df['FL_ID'].isin(final_temp_df.FL_ID)]
                else:
                    continue

            final_temp_df = final_temp_df.append(df)
            df = df[~df['FL_ID'].isin(final_temp_df.FL_ID)]

        return final_temp_df

    '''
    This method combines flights that can be grouped into single duty.
    Only flights with flight time less than 3 hours is considered for
    the grouping. If the flight time is more than 3 hours, combining
    4 flights will give total duty perid of 12+ hours this
    vilotes our total duty period range from 8-12.

    45 minutes added to start and end of every flight OrgUTC and DestUTC

    We're also using 15 minutes for duty period begin and end.
    '''

    def chunk_flights(self, df):
        hour_3 = datetime.timedelta(hours=+3)
        min_15 = datetime.timedelta(minutes=+15)
        split_hours = df.iloc[0].DEST_UTC - df.iloc[0].ORIGIN_UTC
        if split_hours > hour_3:
            return df
        hours = split_hours.seconds//3600
        mins = (split_hours.seconds//60) % 60
        split_hours = float(str(hours)+"."+str(mins))
        tot_flts = round(14/split_hours)
        final_df = pd.DataFrame()
        temp_df = pd.DataFrame()
        i = 0
        df_len = len(df)
        self.logger.debug("DUTY_ID=", self.duty_id)
        while i < df_len:
            flag = True
            for i, g_df in df.groupby(df.index // 2):
                if len(temp_df) == 0:
                    temp_df = temp_df.append(g_df)
                if g_df.iloc[0].ORIGIN_UTC-min_15 > \
                        temp_df.iloc[len(temp_df)-1].DEST_UTC+min_15:
                    temp_df = temp_df.append(g_df)
                    if len(temp_df) < tot_flts and \
                        g_df.iloc[0].FL_DATE == \
                            temp_df.iloc[len(temp_df)-1].FL_DATE:
                        continue
                    else:
                        temp_df["NEW_DUTY_ID"] = self.duty_id
                        df = df[~df['FL_ID'].isin(temp_df.FL_ID)]
                        final_df = final_df.append(temp_df)
                        i = len(final_df)
                        flag = False
                        temp_df = temp_df[0:0]
                        self.duty_id += 1

            if(flag is True):
                final_df = final_df.append(g_df)
                df = df[~df['FL_ID'].isin(g_df.FL_ID)]
                i = len(final_df)

        return final_df

    '''
    Fix the empty newDutyId
    '''

    def fix_dutyNo(self, all_df):
        all_df = all_df.reset_index(drop=True)
        duty_id = 1
        df = pd.DataFrame()
        ind = 0
        all_df['NEW_DUTY_ID'] = all_df['NEW_DUTY_ID'].replace('', np.nan)
        for i, g_df in all_df.groupby(all_df.index // 2):
            if pd.isnull(g_df.loc[ind]['NEW_DUTY_ID']):
                g_df.at[ind, 'NEW_DUTY_ID'] = duty_id
                g_df.at[ind+1, 'NEW_DUTY_ID'] = duty_id+1
                df = df.append(g_df)
                ind += 2
                duty_id += 2
            else:
                temp_id = g_df.loc[ind]['NEW_DUTY_ID']
                g_df.at[ind, 'NEW_DUTY_ID'] = duty_id
                g_df.at[ind+1, 'NEW_DUTY_ID'] = duty_id
                df = df.append(g_df)
                ind += 2
                if np.not_equal(temp_id, all_df.loc[ind]['NEW_DUTY_ID']):
                    duty_id += 1
        return df

    '''
    This method calculates OrgUTC (duty period begin time) and DestUTC
    (duty period end time) Each duty period begin time starts 45 minutes
    before the flight deprature time. Each duty period
    end time ends 45 minutes after flight arrival time
    '''

    def calculate_duty_period(self, all_df):
        final_df = pd.DataFrame()
        duty_id = 1
        min_45 = datetime.timedelta(minutes=+45)
        last_duty_id = all_df.iloc[len(all_df)-1]['NEW_DUTY_ID']
        all_df['ORIGIN_UTC'] = pd.to_datetime(all_df['ORIGIN_UTC'])
        all_df['DEST_UTC'] = pd.to_datetime(all_df['DEST_UTC'])
        all_df['TOT_DUTY_TM'] = ''
        while duty_id < last_duty_id:
            df = all_df[all_df['NEW_DUTY_ID'].isin([duty_id])]
            dtyRepTmUTC = df.iloc[0]['ORIGIN_UTC']-min_45
            dtyRelTmUTC = df.iloc[len(df)-1]['DEST_UTC']+min_45
            df['DUTY_REP_TM_UTC'] = dtyRepTmUTC
            df['DUTY_REL_TM_UTC'] = dtyRelTmUTC
            df['TOT_DUTY_TM'] = dtyRelTmUTC-dtyRepTmUTC
            duty_id += 1
            final_df = final_df.append(df)

        return final_df
