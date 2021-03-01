import crewml.data.feature as fet
import crewml.ml.visual.visualizer as vis
import seaborn as sns
import numpy as np
import itertools

feature = fet.Feature()
feature.load()
feature_names = feature.all_feature_names()
feature_names_combo = list(itertools.combinations(feature_names, 3))

df = feature.numeric_features()
df = df.replace(np.nan, '0', regex=True)
df = df.astype(int)
print(df.dtypes)



cp = vis.CategorialPlot(feature)
cp.plot_univariate(plot_type="count")


'''
import seaborn as sns
tips = sns.load_dataset("tips")
sns.relplot(data=tips, x="total_bill", y="tip", hue="day", col="time",
            row="sex")


feature = fet.Feature()
df = feature.load()
corr = df.corr()
print("df corr=", corr)
rp = vis.DistributionPlot(feature)
# rp.plot_numeric_features(plot_type="line")
rp.plot_numeric_bivariate(plot_type="hist", hue="DEST")



import matplotlib.pyplot as plt
import seaborn as sns

# Subplots are organized in a Rows x Cols Grid
# Tot and Cols are known

Tot = 10
Cols = 3

# Compute Rows required

Rows = Tot // Cols
Rows += Tot % Cols

# Create a Position index

Position = range(1,Tot + 1)

# Create main figure
feature=fet.Feature()
df=feature.load()
num_x_y = feature.get_numeric_x_y()

fig = plt.figure(1)
for k in range(Tot):

  # add every single subplot to the figure with a for loop

  ax = fig.add_subplot(Rows,Cols,Position[k])
  #ax.plot([1,2,3],[4,5,6])      # Or whatever you want in the subplot
  sns.scatterplot(ax=ax, data=df, x=num_x_y[k][0],y=num_x_y[k][1])


plt.show()
'''
