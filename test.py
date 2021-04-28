import crewml.data.feature as fet
import crewml.visual.visualizer as vis

import itertools
import logging.config
import pandas as pd
import numpy as np

import crewml.common as st

logging.config.fileConfig(st.RESOURCE_DIR+'logging.ini',
                          disable_existing_loggers=False)

logger = logging.getLogger(__name__)
x=1 
y="test"

logger.info("this is x=%s and y=%s",x,y)

df = pd.DataFrame(data={'A': [1, 2, 3]}, 
                  index=['a', 'b', 'c'])

df_num= df['A'].tolist()
npa = np.asarray(df_num, dtype=np.int32)

labels = np.array([0, 1, 2, 3])


'''
feature = fet.Feature()
feature.load()
feature_names = feature.all_feature_names()
feature_names_combo = list(itertools.combinations(feature_names, 3))

cp = vis.MultiPlot(feature)
cp.plot(plot_type="joint", hue=True)
'''



