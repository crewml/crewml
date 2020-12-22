# -*- coding: utf-8 -*-
"""
Created on Mon Aug  3 18:21:27 2020

@author: cybel
"""
import Enum

class Location(Enum):
    FILE = 1
    S3 = 2

class DataReader:
    def __init__(self, location):
        if not isinstance(location, Location):
            raise TypeError('location must be an instance of Location Enum')
        print (location.value)

        self.location=location
        
        