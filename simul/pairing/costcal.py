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

import logging
import pandas as pd
import datetime
import setup as st
import traceback

'''
The cost ranges from 0-1000. 0 is no cost for the flight to operate and 1000 is the worst cost
to operate the flight.

1. Flight has to be in a pairing if not it is not a valid flight - cost 1000
2. All pairing must start and end in a base if not - cost 1000
3. Duty time must be 8-14 hours if not  cost - 10\hour more or less 
4. If a flight is not in a pairing - cost 1000
5. If a flight has negative total pairing hours - cost 1000
6. If a flight has a layover - cost 100

All the above rules are checked for each flight. If a flight has 1000 already then a rule is not checked. 
So the maximum cost for a flight will be 1000
'''


class CostCalculator:    
    def __init__(self,input_file,output_file,fa_bases):
        self.logger = logging.getLogger(__name__)
        self.input_file=input_file
        self.output_file=output_file
        self.fa_bases=fa_bases
            
        self.logger.info('info message in CostCalculator')
        
    def process(self):  
        try:
            self.logger.info('info message in CostCalculator process')
            flights_df = pd.read_csv(st.DATA_DIR+self.input_file)
            self.logger.info("flight data read from:", self.input_file)
            flights_df['cost']=0
            
            df=self.check_negative_pairing(flights_df)
            df=self.check_flight_in_pairing(df)
            df=self.check_org_dest_airports(df)
            df=self.check_duty_duration(df)
            df=self.check_layover(df)
            
            df.drop(flights_df.filter(regex="Unname"),axis=1, inplace=True)
            df.to_csv(st.DATA_DIR+self.output_file)
            self.logger.info("flight data write to:", self.output_file)
        except Exception as e:
            self.logger.error(traceback.format_exc())
            raise
        
        
        
    '''
    Check for empty pairinId and store 1000 for cost if it is empty
    '''
    def check_flight_in_pairing(self,df):
        temp=df[df['pairingId'].isnull()]
        temp['cost']=1000
        df=df[~df['fltID'].isin(temp.fltID)]
        df=df.append(temp)
        
        return df
    
    '''
    5. If a flight has negative total pairing hours - cost 1000
    Duty should never be negative, this should be fixed
    '''
    def check_negative_pairing(self,df):
        df['totPairingUTC']=pd.to_timedelta(df['totPairingUTC'])
        
        temp=df[df['totPairingUTC'] < datetime.timedelta(0)]
        temp['cost']=1000
        df=df[~df['fltID'].isin(temp.fltID)]
        df=df.append(temp)
        
        return df
        
    '''    
     All pairing must start and end in a base if not - cost 1000
    '''
    def check_org_dest_airports(self,flights_df):    
        df=pd.DataFrame()
        pairing_id=1
        total=len(flights_df)
        while pairing_id < total:     
            temp=flights_df[flights_df['pairingId'].isin([pairing_id])]
            if len(temp) == 0:
                pairing_id+=1
                continue
    
            h=temp.head(1)
            t=temp.tail(1)         
            orgin_airport=h['Origin'].iloc[0]
            dest_airport=t['Dest'].iloc[0]
            
            if orgin_airport == dest_airport and orgin_airport in self.fa_bases and dest_airport in self.fa_bases :
                pairing_id+=1
                continue
            else:
                #temp['cost'] = temp.apply(add_cost,axis=1)
                temp['cost']=1000 
    
            df=df.append(temp)
            pairing_id+=1
            
        if len(df)!=0:
            temp=flights_df[~flights_df['fltID'].isin(df.fltID)]   
            df=df.append(temp)
        else:
            df=flights_df
            
            
        return df  
    
    '''
    3. Duty time must be 8-14 hours if not  cost - 10\hour more or less 
    '''
    def check_duty_duration(self,flights_df):
        df=pd.DataFrame()
        newDuty_id=1
        total=len(flights_df)
        hour_14=datetime.timedelta(hours=+14)
        flights_df['totDutyTm']=pd.to_timedelta(flights_df['totDutyTm'])
    
        while newDuty_id < total:   
            temp=flights_df[flights_df['newDutyId'].isin([newDuty_id])]
            
            if len(temp) == 0:
                newDuty_id+=1
                continue
            
            h=temp.head(1)
            t=temp.tail(1)    
    
            if h['cost'].iloc[0] == 1000 or t['cost'].iloc[0] == 1000:
                newDuty_id+=1
                continue
            elif h['totDutyTm'].iloc[0] > hour_14:
                tm_dff=(h['totDutyTm'].iloc[0]) 
                #get days and hours. 
                days=tm_dff.days
                hours=tm_dff.seconds//3600
                #convert days to hours and add it to hours and then substract from 14 to  10\hour rule
                tm_dff=(round(days*24+hours)-14)*10
                #if the duty cost comes more than 1000 then change it to 1000. There are many total duty periods
                #comes to 9 days those should be fixed 
                if tm_dff > 1000:
                    tm_dff=1000
                temp['cost']=tm_dff
                
            df=df.append(temp)
            newDuty_id+=1
            
        temp=flights_df[~flights_df['fltID'].isin(df.fltID)]
        
        df=df.append(temp)
            
            
        return df              
    
    '''
    6. If a flight has a layover - cost 100
    '''        
    def check_layover(self,df):
        temp=df[df['layover'].isin(['1']) & df['cost'].isin(['0'])]
        temp['cost']=100
        
        df=df[~df['fltID'].isin(temp.fltID)]
        df=df.append(temp)
        
        return df

