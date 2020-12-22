
import pandas as pd
import logging
import setup as st
import traceback

class PairingGenerator:
        
    def __init__(self,input_file,pairing_gen_missing_files,output_file):
        self.logger=logging.getLogger(__name__)
        self.input_file=input_file
        self.pairing_gen_missing_files=pairing_gen_missing_files
        self.output_file=output_file
        
    
    def process(self):
        try:
            flights_df = pd.read_csv(st.DATA_DIR+self.input_file)
            self.logger.info("flight duty data read from:", self.input_file)
            flights_df.drop(flights_df.filter(regex="Unname"),axis=1, inplace=True)
            final_df=self.create_pairingNo(flights_df)
            final_df=self.create_layover(final_df)
    
            '''
            Add the missing flights to the pairing. All these flights are invalid since they're not in the 
            pairing. There is no duty associated with these flights
            '''
            b2b_miss_df = pd.read_csv(st.DATA_DIR+self.pairing_gen_missing_files[0])
            b2nb_nb2b_miss_df = pd.read_csv(st.DATA_DIR+self.pairing_gen_missing_files[1]) 
            final_df=final_df.append(b2b_miss_df)
            final_df=final_df.append(b2nb_nb2b_miss_df)
            final_df.drop(flights_df.filter(regex="Unname"),axis=1, inplace=True)
            
            final_df.to_csv(st.DATA_DIR+self.output_file)
            self.logger.info("flight pairing data write to:", self.output_file)
        except Exception as e:
            self.logger.error(traceback.format_exc())
            raise
        

    '''
    This method creates flight pairing. Based on the newDutyNo, each pairing will have two duties in it.
    Each duty will have one or more flights which is based on newDutyNo
    '''
    def create_pairingNo(self,flights_df):
        final_df=pd.DataFrame()
        flights_df['dtyRepTmUTC'] = pd.to_datetime(flights_df['dtyRepTmUTC'])
        flights_df['dtyRelTmUTC'] = pd.to_datetime(flights_df['dtyRelTmUTC'])
        pairing_id=1
        new_duty_id=1
        flights_df['pairingId']=''
        flights_df['totPairingUTC']=''
        
        last_new_duty_id=flights_df.loc[len(flights_df)-1,'newDutyId']
        
        while new_duty_id < last_new_duty_id :
            df=flights_df[flights_df['newDutyId'].isin([new_duty_id])]
            df=df.append(flights_df[flights_df['newDutyId'].isin([new_duty_id+1])])
            df['pairingId']=pairing_id
            h_i=df.head(1).index.tolist()[0]
            t_i=df.tail(1).index.tolist()[0]
            
            df['totPairingUTC']=df.loc[t_i,'dtyRelTmUTC']-df.loc[h_i,'dtyRepTmUTC']
            final_df=final_df.append(df)
            pairing_id+=1
            new_duty_id+=2
    
    
        return final_df
    
    
    '''
    Create layover for the flight at the end of the duty if the duty ends not in staring base origin airport
    and if the flight DestUTC falls between 8PM and 6AM. 
    '''    
    def create_layover(self,flights_df):        
        final_df=pd.DataFrame()
        new_duty_id=1
        flights_df['layover']=''
        flights_df['totDutyTm'] = pd.to_timedelta(flights_df['totDutyTm'])
        last_new_duty_id=flights_df['newDutyId'].max()
        flights_df["DestUTC"] = pd.to_datetime(flights_df['DestUTC'])
        
        while new_duty_id < last_new_duty_id :
            df=flights_df[flights_df['newDutyId'].isin([new_duty_id])]
            h_i=df.head(1).index.tolist()[0]
            t_i=df.tail(1).index.tolist()[0]
            
            dest_time_hour = df.loc[h_i,'DestUTC'].hour
            
            if df.loc[h_i,'Origin']!=df.loc[t_i,'Dest'] and (20 <= dest_time_hour or dest_time_hour <= 6 ):
                #add layover=1 only the last flight in the duty. If a duty has 3 flights only the 3rd flight
                #will have the layover=1
                df['layover']=0
                df.at[t_i,'layover']=1
            else:
                df['layover']=0
                
            final_df=final_df.append(df)
            new_duty_id+=1  
            
        return final_df
        



