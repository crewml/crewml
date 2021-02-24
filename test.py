import crewml.data.feature as fet
import crewml.ml.visual.visualizer as vis



feature=fet.Feature()
df=feature.load()
rp=vis.RelationalPlot(feature)
#rp.plot_numeric_features(plot_type="line")
rp.plot_num_cat_features(plot_type="scatter")

'''
import seaborn as sns
tips = sns.load_dataset("tips")
sns.relplot(data=tips, x="total_bill", y="tip", hue="day", col="time", row="sex")
'''

