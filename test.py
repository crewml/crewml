import crewml.data.feature as fet
import crewml.ml.visual.visualizer as vis
import seaborn as sns
import numpy as np
import itertools
import pandas as pd

feature = fet.Feature()
feature.load()
feature_names = feature.all_feature_names()
feature_names_combo = list(itertools.combinations(feature_names, 3))
'''

df = feature.all_features()
df = df.replace(np.nan, '0', regex=True)
#df = df.astype(float)
df["FL_DATE"] = pd.to_datetime(df["FL_DATE"]).dt.strftime("%Y%m%d")
del df['MKT_UNIQUE_CARRIER']


df = df.sample(100)

heatmap_data = pd.pivot_table(df, values='CRS_DEP_TIME', 
                              index=["TAIL_NUM" ], 
                              columns='FL_DATE')
heatmap_data = heatmap_data.replace(np.nan, '0', regex=True)
print(heatmap_data.dtypes)
heatmap_data = heatmap_data.astype(float)
print(heatmap_data.dtypes)

sns.heatmap(heatmap_data)
'''

cp = vis.MultiPlot(feature)
cp.plot(plot_type="joint", hue=True)


