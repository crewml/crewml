# -*- coding: utf-8 -*-
"""
Created on Tue Dec  1 09:16:58 2020


__author__ = "Mani Malarvannan"
__copyright__ ="Copyright 2020 Xcel Energy, Inc"
"""


import configparser
import logging
import traceback
'''
This class reads the configuration data from the passed file names. The file names
must be in *.ini format wih section and parameters below the section
'''



class ConfigHolder:
   section_names=["flight_data"]
 
   def __init__(self, *file_names):
       try:
           self.logger=logging.getLogger(__name__)
           
           parser = configparser.ConfigParser()
           parser.optionxform = str  # make option names case sensitive
           self.logger.debug("Opening config file(s) %s",file_names)
           found = parser.read(file_names)
           
           if not found:
               raise ValueError('No config file(s) found',file_names)
           for name in ConfigHolder.section_names:
                self.__dict__.update(parser.items(name)) 
       except Exception as e:
            self.logger.error(traceback.format_exc())
            raise
            
   def getValue(self,key):
      return self.__dict__.get(key)

'''
ch=ConfigHolder(ROOT_DIR+"\\resources\\pairing_config.ini")   
print(ch.Created_UPDATE12_ELECTRIC_OUTAGE_TROUBLE_TICKET)
print(ch.Updated_Dispatched)
action="Updated_"
event_type="Dispatched"

print("the=",ch.getValue(action+event_type))
'''
    