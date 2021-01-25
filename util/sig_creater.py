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

import hashlib
from crewml.common import DATA_DIR
import os
import zipfile
import logging


class CrewmlUtil:
    
    def create_signature(self,feature):    
        '''
        This function unzips the feature zip files and creates sha256 signature for each file.
        Writes the file name along with the signature in dir DATA_DIR+"/"+feature+"/unzip"

        Parameters
        ----------
        feature : str
            Name of feature to create signature. It can be either flight or pairing

        Returns
        -------
        None.

        '''
        self.logger = logging.getLogger(__name__)
        filelist = []
        BLOCK_SIZE=4096
        path=DATA_DIR+feature
        for root, dirs, files in os.walk(path):
        	for file in files:
                #append the file name to the list
        		filelist.append(os.path.join(root,file))
                
                
        
        for zip_file_name in filelist:
           with zipfile.ZipFile(zip_file_name, 'r') as zip_ref:
               zip_ref.extractall(path+"/unzip")
        
               
        path=DATA_DIR+feature+"/unzip"
        sig_file = open(DATA_DIR+feature+"/"+"signature.txt", "w")
        
        for csv_file_name in filelist:        
           csv_file_name=csv_file_name.split(".")[0]+".csv"
           csv_file_name=os.path.basename(csv_file_name)
           sha256_hash = hashlib.sha256() 
           with open(path+"/"+csv_file_name,"rb") as f:
               for byte_block in iter(lambda: f.read(BLOCK_SIZE),b""):
                   sha256_hash.update(byte_block)
               self.logger.info(sha256_hash.hexdigest())
               sig=os.path.basename(csv_file_name)+"="+sha256_hash.hexdigest()+"\n"
               sig_file.write(sig)
        sig_file.close()

ut=CrewmlUtil()
ut.create_signature("flight")
