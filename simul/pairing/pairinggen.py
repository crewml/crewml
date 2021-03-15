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
import crewml.common as st
import traceback

'''
This class takes duty file and generates Pairing by combining the duties
'''


class PairingGenerator:

    def __init__(self, input_file, pairing_gen_missing_files, output_file):
        self.logger = logging.getLogger(__name__)
        self.input_file = input_file
        self.pairing_gen_missing_files = pairing_gen_missing_files
        self.output_file = output_file

    def process(self):
        try:
            flights_df = pd.read_csv(st.DATA_DIR+self.input_file)
            self.logger.info("flight duty data read from:", self.input_file)
            flights_df.drop(flights_df.filter(
                regex="Unname"), axis=1, inplace=True)
            final_df = self.create_pairingNo(flights_df)
            final_df = self.create_layover(final_df)

            '''
            Add the missing flights to the pairing. All these flights
            are invalid since they're not in the
            pairing. There is no duty associated with these flights
            '''
            b2b_miss_df = pd.read_csv(
                st.DATA_DIR+self.pairing_gen_missing_files[0])
            b2nb_nb2b_miss_df = pd.read_csv(
                st.DATA_DIR+self.pairing_gen_missing_files[1])
            final_df = final_df.append(b2b_miss_df)
            final_df = final_df.append(b2nb_nb2b_miss_df)
            final_df.drop(flights_df.filter(
                regex="Unname"), axis=1, inplace=True)

            final_df.to_csv(st.DATA_DIR+self.output_file)
            self.logger.info("flight pairing data write to:", self.output_file)
        except Exception as e:
            self.logger.error(traceback.format_exc())
            raise

    '''
    This method creates flight pairing. Based on the newDutyNo,
    each pairing will have two duties in it.
    Each duty will have one or more flights which is based on newDutyNo
    '''

    def create_pairingNo(self, flights_df):
        final_df = pd.DataFrame()
        flights_df['DUTY_REP_TM_UTC'] = pd.to_datetime(flights_df['DUTY_REP_TM_UTC'])
        flights_df['DUTY_REL_TM_UTC'] = pd.to_datetime(flights_df['DUTY_REL_TM_UTC'])
        pairing_id = 1
        new_duty_id = 1
        flights_df['PAIRING_ID'] = ''
        flights_df['TOT_PAIRING_UTC'] = ''

        last_new_duty_id = flights_df.loc[len(flights_df)-1, 'NEW_DUTY_ID']

        while new_duty_id < last_new_duty_id:
            df = flights_df[flights_df['NEW_DUTY_ID'].isin([new_duty_id])]
            df = df.append(
                flights_df[flights_df['NEW_DUTY_ID'].isin([new_duty_id+1])])
            df['PAIRING_ID'] = pairing_id
            h_i = df.head(1).index.tolist()[0]
            t_i = df.tail(1).index.tolist()[0]

            df['TOT_PAIRING_UTC'] = df.loc[t_i, 'DUTY_REL_TM_UTC'] - \
                df.loc[h_i, 'DUTY_REP_TM_UTC']
            final_df = final_df.append(df)
            pairing_id += 1
            new_duty_id += 2

        return final_df

    '''
    Create layover for the flight at the end of the duty if the
    duty ends not in staring base origin airport
    and if the flight DestUTC falls between 8PM and 6AM.
    '''

    def create_layover(self, flights_df):
        final_df = pd.DataFrame()
        new_duty_id = 1
        flights_df['LAYOVER'] = ''
        flights_df['TOT_DUTY_TM'] = pd.to_timedelta(flights_df['TOT_DUTY_TM'])
        last_new_duty_id = flights_df['NEW_DUTY_ID'].max()
        flights_df["DEST_UTC"] = pd.to_datetime(flights_df['DEST_UTC'])

        while new_duty_id < last_new_duty_id:
            df = flights_df[flights_df['NEW_DUTY_ID'].isin([new_duty_id])]
            h_i = df.head(1).index.tolist()[0]
            t_i = df.tail(1).index.tolist()[0]

            dest_time_hour = df.loc[h_i, 'DEST_UTC'].hour

            if df.loc[h_i, 'ORIGIN'] != df.loc[t_i, 'DEST'] and \
                    (20 <= dest_time_hour or dest_time_hour <= 6):
                # add layover=1 only the last flight in the duty. If a
                # duty has 3 flights only the 3rd flight
                # will have the layover=1
                df['LAYOVER'] = 0
                df.at[t_i, 'LAYOVER'] = 1
            else:
                df['LAYOVER'] = 0

            final_df = final_df.append(df)
            new_duty_id += 1

        return final_df
