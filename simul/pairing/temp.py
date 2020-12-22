# -*- coding: utf-8 -*-
"""
Created on Sun Dec 13 18:10:40 2020

@author: cybel
"""
import os.path

from simul.pairing import flclean as fl

data_path=os.path.dirname(__file__)

'''
Create FlightCleaner object, load the flights, use the timezone to convert the local departure and arrival time to
UTC time
'''
inp=data_path+"\\data\\flights_feb2020_dl.csv"
tz=data_path+"\\data\\timezones.csv"
output=data_path+"\\data\\flights_cleaned.csv"
fc=fl.FlightCleaner(inp,tz,output) 
