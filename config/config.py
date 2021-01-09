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


    