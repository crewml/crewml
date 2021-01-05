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

import traceback
import os.path
import setup as st
from config import config
from ml import prvisualize as prv

def main():
    try:
        logger = logging.getLogger(__name__)
    
    
        logger.info("Starting main")
        
        data_path=os.path.dirname(__file__)
        
        ch=config.ConfigHolder(data_path+"/config/resources/pairing_config.ini")


        pairing_input_file=ch.getValue("cost_cal_output_file")
        pv=prv.PairingVisualizer(pairing_input_file)
        pv.process()
        pv.plot_box()
        pv.encode_pairing_feature()

        pv.plot_histogram()
        pv.plot_scatter("Dest")
        pv.plot_pivot("Dest")
        pv.plot_pair("Dest")

        
        logger.info("Finished main")
    except Exception as e: 
        logger.error(traceback.format_exc())

    
if __name__ == '__main__':
    import logging.config
    logging.config.fileConfig(st.LOG_DIR+'logging.ini',disable_existing_loggers=False)

    main()

