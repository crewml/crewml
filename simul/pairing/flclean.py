#!/usr/bin/python
# -*- coding: utf-8 -*-

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
import traceback
import calendar
import datetime
import pytz
import logging.config
from crewml.common import DATA_DIR


class FlightCleaner:
    '''
    AIR_TIME	- Flight Time, in Minutes 
    CRS_ELAPSED_TIME	- CRS Elapsed Time of Flight, in Minutes
    DEST	- Destination airport
    ORIGIN  - Origin Airport
    DEST_UTC	- Destination time in UTC
    DISTANCE	- Distance between airports (miles)
    FL_DATE		- Flight departure date
    ORIGIN_UTC	- Flight departure time in UTC


    '''
    def __init__(
        self,
        feature,
        timezone_file_name,
        output_file_name,
    ):

        self.logger = logging.getLogger(__name__)
        self.timezone_file_name = timezone_file_name
        self.output_file_name = output_file_name
        self.feature = feature

        self.flights_df = feature.load()

        # Read timezones for airport iata_code

        self.tz_df = pd.read_csv(DATA_DIR + self.timezone_file_name)
        self.logger.info('Timezone loaded:', self.timezone_file_name)

    # Read the input flight data from file

    def process(self):
        try:
            self.flights_df = self.flights_df.dropna()

            # create unique id for each flight (row)

            self.flights_df.insert(0, 'FL_ID',
                                   self.flights_df.reset_index().index)

            self.flights_df['FL_DATE'] = \
                pd.to_datetime(self.flights_df['FL_DATE'])

            self.flights_df['FL_DATE'] = \
                self.flights_df['FL_DATE'].dt.strftime('%m/%d/%Y')

            self.flights_df["FL_KEY"] = self.flights_df["FL_DATE"].astype(
                str) + self.flights_df["ORIGIN"] + self.flights_df["DEST"]

            self.logger.info('total flights DataFrame shape=',
                             self.flights_df.shape)

            # find timeZones for departure and arrival flight time

            (self.flights_df['ORIGIN_TZ'], self.flights_df['DEST_TZ'
                                                           ]) = zip(*self.flights_df.apply(lambda x:
                                                                                           self.calculateTimeZone(
                                                                                               x['ORIGIN'], x['DEST']),
                                                                                           axis=1))

            # cacluate flight time and convert orgin and destination
            # local time to UTC

            (self.flights_df['AIR_TIME'], self.flights_df['ORIGIN_UTC'
                                                          ], self.flights_df['DEST_UTC']) = \
                zip(*self.flights_df.apply(lambda x:
                                           self.calculateFltTime(x['FL_DATE'], x['CRS_DEP_TIME'
                                                                                 ], x['CRS_ARR_TIME'], x['ORIGIN_TZ'], x['DEST_TZ'
                                                                                                                         ]), axis=1))

            self.flights_df.to_csv(DATA_DIR + self.output_file_name)
            self.logger.info('File created:%s and size %s',
                             self.output_file_name, len(self.flights_df))
        except Exception as e:

            self.logger.error(traceback.format_exc())
            raise

    def read_flights(self):

        # Feb 2020 flight data for Delta Airlines

        self.flights_df = pd.read_csv(DATA_DIR + self.input_file_name,
                                      dtype='unicode')
        self.logger.info('Raw fligh data loaded:', self.input_file_name)

        # Read timezones for airport iata_code

        self.tz_df = pd.read_csv(DATA_DIR + self.timezone_file_name)
        self.logger.info('Timezone loaded:', self.timezone_file_name)

    def remove_elements(self):
        self.flights_df = self.flights_df[self.elements]

    def calculateTimeZone(self, x, y):
        temp1 = self.tz_df.loc[self.tz_df['iata_code'] == x, 'iana_tz'
                               ].values
        temp2 = self.tz_df.loc[self.tz_df['iata_code'] == y, 'iana_tz'
                               ].values

        return (temp1[0], temp2[0])

    def calculateFltTime(
        self,
        x,
        y,
        z,
        tz1,
        tz2,
    ):

        timezone1 = pytz.timezone(tz1)
        timezone2 = pytz.timezone(tz2)

        self.logger.info("x=%s,y=%s,z=%s,tz1=%s,tz2=%s" % (x,y,z,tz1,tz2))
        flt_dt = datetime.datetime.strptime(x, '%m/%d/%Y')

        y = str(int(y)).zfill(4)
        z = str(int(z)).zfill(4)
        y_hour = int(y[0:2])
        y_min = int(y[2:4])
        z_hour = int(z[0:2])
        z_min = int(z[2:4])
        if y_hour > 1:
            y_hour = y_hour - 1
        if z_hour > 1:
            z_hour = z_hour - 1

        dt1 = timezone1.localize(datetime.datetime(
            flt_dt.year,
            flt_dt.month,
            flt_dt.day,
            y_hour,
            y_min,
            0,
            0,
        ))
        dt2 = timezone2.localize(datetime.datetime(
            flt_dt.year,
            flt_dt.month,
            flt_dt.day,
            z_hour,
            z_min,
            0,
            0,
        ))

        dt1_utc = dt1.astimezone(pytz.utc)
        dt2_utc = dt2.astimezone(pytz.utc)

        tot_days = calendar.monthrange(flt_dt.year, flt_dt.month)[1]
        if dt1 > dt2:
            if tot_days == flt_dt.day:
                month = flt_dt.month + 1
                day = 1
            else:
                month = flt_dt.month
                day = flt_dt.day + 1

            if month > 12:
                month=12
                self.logger.info("month greater than 12. month=%s,day=%s,z_hour=%s,z_min=%s" % (month,day,z_hour,z_min))
                
            dt2 = timezone2.localize(datetime.datetime(
                flt_dt.year,
                month,
                day,
                z_hour,
                z_min,
                0,
                0,
            ))
            dt2_utc = dt2.astimezone(pytz.utc)

        flt_time = dt2 - dt1

        return (flt_time, dt1_utc, dt2_utc)
