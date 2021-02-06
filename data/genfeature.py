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
import logging
import pandas as pd
import os
import numpy as np
import matplotlib.pyplot as plt

from crewml.config import config
import crewml.common as st
from crewml.exception import CrewmlDataError

class GenericFeature:
    '''
    '''
    
    def __init__(self,feature_name="flight", load_dir=None, file_name=None):
        self.logger = logging.getLogger(__name__)
        self.con=config.ConfigHolder(st.RESOURCE_DIR+"pairing_config.ini")
        self.feature_name=feature_name
        self.df=None
        self.flight_features=self.con.getValue("flight_features")
        self.flight_features=self.flight_features.split(",")
        self.preferred_airline_code=self.con.getValue("preferred_airline_code")
        if load_dir == None :
            self.load_dir=st.ROOT_DIR+self.con.getValue("download_dir")
        else:
            self.load_dir=load_dir
        
        if file_name==None :    
            files = os.listdir(self.load_dir)
            files = list(filter(lambda x: x.find(".csv") !=-1, files))
            paths = [os.path.join(self.load_dir, basename) for basename in files]
            self.file_name=max(paths, key=os.path.getctime)

        else:
            self.file_name=file_name
        
        if self.file_name ==None:
            raise CrewmlDataError("No file exist in "+load_dir)
        
        
    def load(self):       
        self.df = pd.read_csv(self.file_name, usecols=self.flight_features)
        self.df = self.df[self.df.MKT_UNIQUE_CARRIER == self.preferred_airline_code]
        self.df = self.df.reset_index(drop=True)
        return self.df
        
        
    
    def features(self):
        return self.df
    
'''    
gf=GenericFeature()    
flight_df=gf.load()
flight_df.to_csv("flights.csv")
'''
import seaborn as sns

flight_df=pd.read_csv("flights.csv")
flight_df['FL_DATE']=pd.to_datetime(flight_df['FL_DATE'])
flight_df=flight_df.sample(100)
nan_val=flight_df.isnull().values.any()
flight_df=flight_df.fillna(0)
flight_df = flight_df.loc[:, ~flight_df.columns.str.contains('^Unnamed')]
sns.set(style="whitegrid", font_scale=0.1)
#sns.set_theme(style="darkgrid", font_scale=0.1,palette="deep")
sns.set_context("paper")
'''
For sns.displot
sns.displot(data=flight_df, x="ORIGIN")
kind="kde" needs the x feature must be date/numeric
rug=True needs x feature must be Numeric

Currently, bivariate plots (x and y) are available only for histograms and KDEs:
'''
#sns.displot(data=flight_df, x="DISTANCE", hue="DEST",  kind="kde")
#sns.displot(data=flight_df, x="DISTANCE", hue="DEST",   multiple="stack")
#sns.displot(data=flight_df, x="DISTANCE", col="DEST", aspect=.7, multiple="stack")
#sns.relplot(data=flight_df, x="DISTANCE", y="TAIL_NUM", row="DEST", hue="ORIGIN", col="AIR_TIME") #hangs
#sns.relplot(data=flight_df, kind="line") #only numeric/date
#sns.scatterplot(data=flight_df, x="FL_DATE", y="DISTANCE", style="DEST", hue="CRS_DEP_TIME")
#sns.lineplot(data=flight_df, x="FL_DATE", y="DISTANCE", style="DEST", hue="CRS_DEP_TIME") good one
'''
sns.lineplot(
    data=flight_df, x="FL_DATE", y="DISTANCE",
    hue="ORIGIN")  confulsing lines

sns.lineplot(
    data=flight_df, x="FL_DATE", y="DISTANCE", hue="DEST", style="ORIGIN",
)

palette = sns.color_palette("mako_r", 6)
sns.lineplot(
    data=flight_df.query("DISTANCE > 1000"),
    x="FL_DATE", y="AIR_TIME", hue="DISTANCE", style="CRS_ELAPSED_TIME",
     palette="flare", hue_norm=mpl.colors.LogNorm(),
)

sns.histplot(data=flight_df, x="DISTANCE")
sns.histplot(data=flight_df, y="DISTANCE")
sns.histplot(data=flight_df, x="DISTANCE",binwidth=3)
sns.histplot(data=flight_df, x="DISTANCE",bins=30, kde=True)
sns.histplot(data=flight_df)

sns.histplot(data=flight_df, x="DISTANCE", hue="FL_DATE")
sns.histplot(data=flight_df, x="DISTANCE", hue="FL_DATE", multiple="stack")
sns.histplot(data=flight_df, x="DISTANCE", hue="FL_DATE", element="poly")
sns.histplot(flight_df, x="DISTANCE", y="FL_DATE", hue="DEST")
sns.ecdfplot(data=flight_df, x="DISTANCE", hue="FL_DATE", complementary=True)
'''
#sns.kdeplot(data=flight_df)
#sns.kdeplot(data=flight_df,x="DISTANCE")
#sns.kdeplot(data=flight_df,x="DISTANCE", y="FL_DATE")

#sns.rugplot(data=flight_df)
#sns.rugplot(data=flight_df,x="DISTANCE")

#sns.scatterplot(data=flight_df,x="DISTANCE", y="FL_DATE")
#sns.rugplot(data=flight_df,x="DISTANCE", y="FL_DATE")

#sns.scatterplot(data=flight_df,x="DISTANCE", y="FL_DATE", s=5)
#sns.rugplot(data=flight_df,x="DISTANCE", y="FL_DATE",lw=1, alpha=.005)


'''

sns.set_theme(style="ticks")
sns.set_context("paper", rc={"font.size":4,"axes.titlesize":4,"axes.labelsize":10}) 
g = sns.catplot(x="FL_DATE", y="DISTANCE", hue="DEST", kind="violin",data=flight_df)
'''
#ax = sns.boxplot(x=flight_df["DISTANCE"])
#ax = sns.boxplot(data=flight_df,x="DISTANCE",y="FL_DATE")
#ax = sns.swarmplot(data=flight_df,x="DISTANCE",y="FL_DATE")
#ax = sns.boxenplot(data=flight_df,x="DISTANCE",y="FL_DATE")
#ax = sns.barplot(data=flight_df,x="DISTANCE",y="FL_DATE")
#ax = sns.countplot(data=flight_df)
'''
heatmap needs all float values

flight_df=flight_df.drop('FL_DATE', axis=1)
flight_df=flight_df.drop('MKT_UNIQUE_CARRIER', axis=1)
flight_df=flight_df.drop('TAIL_NUM', axis=1)
flight_df=flight_df.drop('DEST', axis=1)
flight_df=flight_df.drop('ORIGIN', axis=1)
flight_df.reindex()
#ax = sns.heatmap(data=flight_df)
#ax = sns.heatmap(data=flight_df, vmin=0, vmax=1)
ax = sns.heatmap(data=flight_df,  center=0, cmap="YlGnBu")
'''
#g = sns.clustermap(data=flight_df)
#g = sns.clustermap(flight_df,figsize=(7, 5), row_cluster=False,dendrogram_ratio=(.1, .2),cbar_pos=(0, .2, .03, .4))
#g = sns.clustermap(flight_df, cmap="mako", vmin=0, vmax=10)

#g = sns.pairplot(data=flight_df)
#g = sns.pairplot(data=flight_df,hue="DEST")
#g = sns.pairplot(data=flight_df,hue="FL_DATE",diag_kind="hist")
#g = sns.pairplot(data=flight_df,kind="kde")
#g = sns.pairplot(data=flight_df,kind="hist")

'''
g = sns.PairGrid(flight_df)
g.map(sns.scatterplot)
'''

'''
g = sns.PairGrid(flight_df)
g.map_diag(sns.histplot)
g.map_offdiag(sns.scatterplot)
'''

'''
g = sns.PairGrid(flight_df, diag_sharey=False)
g.map_upper(sns.scatterplot)
g.map_lower(sns.kdeplot)
g.map_diag(sns.kdeplot)
'''

'''
g = sns.PairGrid(flight_df, diag_sharey=False, corner=True)
g.map_lower(sns.scatterplot)
g.map_diag(sns.kdeplot)
'''

'''
g = sns.PairGrid(flight_df, hue="DISTANCE")
g.map_diag(sns.histplot)
g.map_offdiag(sns.scatterplot)
g.add_legend()
'''
'''
g = sns.PairGrid(flight_df, hue="DISTANCE")
g.map_diag(plt.hist)
g.map_offdiag(plt.scatter)
g.add_legend()
'''

'''
g = sns.PairGrid(flight_df, hue="DISTANCE")
g.map_diag(sns.histplot)
g.map_offdiag(sns.scatterplot, size=flight_df["DEST"])
g.add_legend(title="", adjust_subtitles=True)
'''

#sns.jointplot(data=flight_df, x="FL_DATE", y="DEST")
#sns.jointplot(data=flight_df, x="FL_DATE", y="DISTANCE", hue="DEST")


'''
Need target value
#sns.jointplot(data=flight_df, x="CRS_DEP_TIME", y="DISTANCE", hue="AIR_TIME", kind="kde")
'''

#sns.jointplot(data=flight_df, x="CRS_DEP_TIME", y="DISTANCE", hue="AIR_TIME", kind="hist")
#sns.jointplot(data=flight_df, x="CRS_DEP_TIME", y="DISTANCE",  kind="hex")
#sns.jointplot(data=flight_df, x="CRS_DEP_TIME", y="DISTANCE",  marker="+", s=100, marginal_kws=dict(bins=25, fill=False))
#sns.jointplot(data=flight_df, x="CRS_DEP_TIME", y="DISTANCE", height=5, ratio=2, marginal_ticks=True)
#g=sns.jointplot(data=flight_df, x="CRS_DEP_TIME", y="DISTANCE", height=5, ratio=2, marginal_ticks=True)

'''
g = sns.jointplot(data=flight_df, x="CRS_DEP_TIME", y="DISTANCE")
g.plot_joint(sns.kdeplot, color="r", zorder=0, levels=6)
g.plot_marginals(sns.rugplot, color="r", height=-.15, clip_on=False)
'''
'''
sns.JointGrid(data=flight_df, x="CRS_DEP_TIME", y="DISTANCE")
g = sns.JointGrid(data=flight_df, x="CRS_DEP_TIME", y="DISTANCE")
#g.plot(sns.scatterplot, sns.histplot)
#g.plot(sns.scatterplot, sns.histplot, alpha=.7, edgecolor=".2", linewidth=.5)
g.plot_marginals(sns.histplot, kde=True)
'''

'''
g = sns.JointGrid()
x, y = flight_df["CRS_DEP_TIME"], flight_df["DISTANCE"]
sns.scatterplot(x=x, y=y, ec="b", fc="none", s=100, linewidth=1.5, ax=g.ax_joint)
sns.histplot(x=x, fill=False, linewidth=2, ax=g.ax_marg_x)
sns.kdeplot(y=y, linewidth=2, ax=g.ax_marg_y)
'''

'''
g = sns.JointGrid(data=flight_df, x="CRS_DEP_TIME", y="DISTANCE")
g.plot(sns.regplot, sns.boxplot)
'''

'''
g = sns.JointGrid(data=flight_df, x="CRS_DEP_TIME", y="DISTANCE", hue="AIR_TIME")
g.plot(sns.scatterplot, sns.histplot)
'''

#g = sns.lmplot(x="CRS_DEP_TIME", y="DISTANCE", hue="AIR_TIME", data=flight_df)
#g = sns.regplot(x="CRS_DEP_TIME", y="DISTANCE", data=flight_df, color="r", marker="+")
g = sns.regplot(x="CRS_DEP_TIME", y="DISTANCE", data=flight_df, color="r", marker="+",x_estimator=np.mean)





























'''
flight_df=flight_df.drop(["FL_DATE","MKT_UNIQUE_CARRIER","TAIL_NUM","DEST","ORIGIN"], axis=1, inplace=True)
'''




