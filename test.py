import crewml.data.feature as fet
import crewml.ml.visual.visualizer as vis

import itertools


feature = fet.Feature()
feature.load()
feature_names = feature.all_feature_names()
feature_names_combo = list(itertools.combinations(feature_names, 3))

cp = vis.MultiPlot(feature)
cp.plot(plot_type="joint", hue=True)
