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
import crewml.common as st
from crewml.config import config
from crewml.ml.super import prlogreg as prlg
from crewml.ml.super import prmoddep as pmd


def main():
    '''
    Main function to to execute ML package

    Returns
    -------
    None.

    '''

    try:
        logger = logging.getLogger(__name__)

        logger.info("Starting main")

        ch = config.ConfigHolder(st.RESOURCE_DIR+"pairing_config.ini")
        pairing_month = ch.getValue("pairing_month")
        pairing_input_file = ch.getValue("cost_cal_output_file")
        pairing_model_output_file = ch.getValue("pairing_model_output_file")

        '''
        Use PairingRegressor to create Regression Model

        pr=prr.PairingRegressor(pairing_input_file)
        pr.process()
        pr.split_feature()
        pr.perfom_decision_tree_regressor()
        pr.perform_xgboost_regressor()
        '''

        '''
        Use PairingLogRegressor to crete Logistic Regression Model
        '''

        plr = prlg.PairingLogRegressor(pairing_input_file,
                                       pairing_month,
                                       pairing_model_output_file)
        plr.process()
        selected_pairings = plr.get_selected_pairings()
        print("flight_id=%s and pairing_id=%s"
              % (selected_pairings["FL_ID"].tolist(),
                 selected_pairings["PAIRING_ID"].tolist()
                 ))
        plr.split_feature()
        # plr.decision_tree_classifier()
        # plr.gradient_boost_classifier()
        # plr.random_forest_classifier()
        # plr.xgboost_model_parms()
        plr.xgboost_classifier()

        '''
        flights=plr.select_pairings(100)
        pairing_model_file=ch.getValue("pairing_model_file")      
        prmodel=pmd.PairingModelDeployer(pairing_model_file)
        prmodel.predict_pairings(flights)
        '''

        logger.info("Finished main")
    except Exception as e:
        logger.error(traceback.format_exc())


if __name__ == '__main__':
    import logging.config
    logging.config.fileConfig(
        st.RESOURCE_DIR+'logging.ini', disable_existing_loggers=False)

    main()
