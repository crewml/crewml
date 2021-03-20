import crewml.data.feature as fet
import crewml.visual.visualizer as vis

import itertools
import logging.config

import crewml.common as st

logging.config.fileConfig(st.RESOURCE_DIR+'logging.ini',
                          disable_existing_loggers=False)

logger = logging.getLogger(__name__)
x=1 
y="test"

logger.info("this is x=%s and y=%s",x,y)


'''
feature = fet.Feature()
feature.load()
feature_names = feature.all_feature_names()
feature_names_combo = list(itertools.combinations(feature_names, 3))

cp = vis.MultiPlot(feature)
cp.plot(plot_type="joint", hue=True)
'''

import pandas as pd
import numpy as np
dates = pd.date_range('1/1/2000', periods=8)
df = pd.DataFrame(np.random.randn(8, 4), index=dates, columns=['A', 'B', 'C', 'D'])
s = df['A']