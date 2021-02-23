import crewml.data.feature as fet
import crewml.ml.visual.visualizer as vis



feature=fet.Feature()
df=feature.load()
rp=vis.RelationalPlot(feature)
rp.plot_numeric_features(plot_type="line")






