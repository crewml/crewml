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
import sys,os
import calendar
import datetime
import pytz
import logging.config
from setup import DATA_DIR

'''
This program reads flight data, and converts all the local timestamp to UTC and removes
unnecessary data. Each row contains a specific flight. 

All the flight data is downloaded from https://www.transtats.bts.gov/Tables.asp?DB_ID=120&DB_Name=Airline%20On-Time%20Performance%20Data&DB_Short_Name=On-T

FlightDate	- Fligh Departure Date
Tail_Number	- Unique registeration number that identifies a equipment, given by FAA
Origin	 - Origin Airport
Dest	 - Destination Airport
DepTime  - Local Departure Time in hours and minutes 	
ArrTime	 - Local Arrival Time in hours and minutes
Distance - Distance in miles between Depature and Arrival airports

'''



class FlightCleaner:
    
    def __init__(self, file1,file2,file3,elements,column_name,airline_code):
        self.logger = logging.getLogger(__name__)
        self.input_file_name=file1
        self.timezone_file_name=file2
        self.output_file_name=file3
        self.elements=elements
        self.column_name=column_name
        self.airline_code=airline_code
        self.flights_df=None
        
        
    
    #Read the input flight data from file
    def process(self):
        try:
            self.read_flights()
            self.remove_elements()
            self.flights_df = self.flights_df[self.flights_df.eval(self.column_name) == self.airline_code]
            self.flights_df= self.flights_df.dropna()
            
            #create unique id for each flight (row)
            self.flights_df.insert(0, "fltID",self.flights_df.reset_index().index)
            self.logger.info("total flights DataFrame shape=",self.flights_df.shape)
            
            #find timeZones for departure and arrival flight time
            self.flights_df["DepTz"], self.flights_df["ArrTz"] = zip(*self.flights_df.apply(lambda x: self.calculateTimeZone(x['Origin'], x['Dest']), axis=1))
    
            #cacluate flight time and convert orgion and destination local time to UTC
            self.flights_df["FltTime"], self.flights_df["OrgUTC"], self.flights_df["DestUTC"] = zip(*self.flights_df.apply(lambda x: self.calculateFltTime(x['FlightDate'], x['DepTime'], x['ArrTime'],x["DepTz"],x["ArrTz"]), axis=1))
        
            self.flights_df.to_csv(DATA_DIR+self.output_file_name)
            self.logger.info("Filecreated:", self.output_file_name)
        except Exception as e:
            self.logger.error(traceback.format_exc())
            raise
        
    '''
    Function reads flight data from file
    '''
    def read_flights(self):  
        #Feb 2020 flight data for Delta Airlines 
        self.flights_df = pd.read_csv(DATA_DIR+self.input_file_name, dtype='unicode')      
        self.logger.info("Raw fligh data loaded:", self.input_file_name)
        
        #Read timezones for airport iata_code
        self.tz_df = pd.read_csv(DATA_DIR+self.timezone_file_name)
        self.logger.info("Timezone loaded:", self.timezone_file_name)


        
        

    '''
    Retain only the elements specified in the element list passed in the __int__ method
    '''    
    def remove_elements(self):
        self.flights_df=self.flights_df[self.elements]


    '''
    Calculate TimeZones for the origin and destination local time for the flights
    '''
    def calculateTimeZone(self,x,y):
        temp1=(self.tz_df.loc[self.tz_df['iata_code'] == x, 'iana_tz']).values
        temp2=(self.tz_df.loc[self.tz_df['iata_code'] == y, 'iana_tz']).values        
    
        return temp1[0],temp2[0]


    '''
    This function calculates flight time and converts local departure and arrival time to UTC for
    flight
    '''
    def calculateFltTime(self,x,y,z,tz1,tz2):
            
        timezone1 = pytz.timezone(tz1)
        timezone2 = pytz.timezone(tz2)
        FlightCleaner.logger.info("x=",x,"y=",y,"z=",z,"tz1=",tz1,"tz2=",tz2)

        flt_dt = datetime.datetime.strptime(x, "%Y-%m-%d")
    
        y=str(int(y)).zfill(4)
        z=str(int(z)).zfill(4)
        y_hour=int(y[0:2])
        y_min=int(y[2:4])
        z_hour=int(z[0:2])
        z_min=int(z[2:4])    
        if y_hour > 1:
            y_hour=y_hour-1
        if z_hour > 1:
            z_hour=z_hour-1    
        
        dt1= timezone1.localize(datetime.datetime(flt_dt.year,flt_dt.month, flt_dt.day, y_hour,y_min, 0, 0))
        dt2= timezone2.localize(datetime.datetime(flt_dt.year,flt_dt.month, flt_dt.day, z_hour,z_min, 0, 0))
        
        dt1_utc=dt1.astimezone(pytz.utc) 
        dt2_utc=dt2.astimezone(pytz.utc) 
        
            
        tot_days=calendar.monthrange(flt_dt.year, flt_dt.month)[1]
        if dt1 > dt2  :     
            if tot_days == flt_dt.day :
                month=flt_dt.month+1
                day=1
            else:
                month=flt_dt.month
                day=flt_dt.day+1 
            dt2= timezone2.localize(datetime.datetime(flt_dt.year,month, day, z_hour, z_min, 0, 0)) 
            dt2_utc=dt2.astimezone(pytz.utc) 
        
        flt_time=(dt2-dt1) 
        
        return flt_time, dt1_utc, dt2_utc 


    

