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

import pandas as pd
import os.path
import numpy as np
import matplotlib.pyplot as plt
from category_encoders import TargetEncoder
import seaborn as sns
from sklearn.feature_selection import f_regression, mutual_info_regression
from scipy import stats
from crewml.common import DATA_DIR
import logging


'''
feature selection methods
Filter methods
    chi square
    Anova Test
    Corralation coefficient
Wrapper Methods
    Forward selection
    Backward selection
    Recursive feature elemination
Embeeded Method

Mutual Selection (non-linear models)

'''


class PairingVisualizer:
    def __init__(self, feature_file):
        '''
        Create PairingVisualizer with feature file

        Parameters
        ----------
        feature_file : TYPE
            Feature file that has pairing data that needs to be visualized

        Returns
        -------
        None.

        '''

        self.logger = logging.getLogger(__name__)
        self.feature_file = feature_file
        self.pairing_df = None

        print("feature_file=", feature_file)

    def process(self):
        '''
        process pairing data and prepare for visualization

        Returns
        -------
        None.

        '''
        self.pairing_df = pd.read_csv(DATA_DIR+self.feature_file)
        self.logger.info("Pairing data read from:", self.feature_file)

        self.pairing_df.drop(self.pairing_df.filter(
            regex="Unname"), axis=1, inplace=True)

        # convert time to seconds
        self.pairing_df['FltTime'] = pd.to_timedelta(
            self.pairing_df['FltTime']).dt.seconds
        self.pairing_df['totDutyTm'] = pd.to_timedelta(
            self.pairing_df['totDutyTm']).dt.seconds
        self.pairing_df['totPairingUTC'] = pd.to_timedelta(
            self.pairing_df['totPairingUTC']).dt.seconds

        # convert datetime into second
        self.pairing_df['OrgUTC'] = pd.to_datetime(self.pairing_df['OrgUTC'])
        self.pairing_df['OrgUTC'] = self.pairing_df.OrgUTC.astype(int)

        self.pairing_df['DestUTC'] = pd.to_datetime(self.pairing_df['DestUTC'])
        self.pairing_df['DestUTC'] = self.pairing_df.OrgUTC.astype(int)

        self.pairing_df['dtyRelTmUTC'] = pd.to_datetime(
            self.pairing_df['dtyRelTmUTC'])
        self.pairing_df['dtyRelTmUTC'] = self.pairing_df.dtyRelTmUTC.astype(
            int)

        self.pairing_df['dtyRepTmUTC'] = pd.to_datetime(
            self.pairing_df['dtyRepTmUTC'])
        self.pairing_df['dtyRepTmUTC'] = self.pairing_df.OrgUTC.astype(int)

        # Convert flight date to int
        self.pairing_df['FlightDate'] = self.pairing_df['FlightDate'].astype(
            str)

        self.pairing_df['FlightDate'] = self.pairing_df.FlightDate.str.replace(
            "-", "").astype(int)

    '''
    Create box plot for the pairing data retrieved and processed from the process
    function
    '''

    def plot_box(self):
        '''
        Display box plot of pairing data

        Returns
        -------
        None.

        '''
        self.pairing_df.groupby('Origin').boxplot(
            fontsize=15, rot=50, figsize=(30, 30), patch_artist=True)
        plt.show()

    def encode_pairing_feature(self):
        '''
        Use the TargetEncoder to encode Origin, Dest, TailNumber features, these
        feature has alphanumeric and this function converts it to numeric using
        TargetEncoder

        Returns
        -------
        None.

        '''
        temp1 = self.pairing_df[self.pairing_df['pairingId'].isnull()]
        temp1['pairingId'] = 0
        temp2 = self.pairing_df[~self.pairing_df['fltID'].isin(temp1.fltID)]
        temp2['pairingId'] = 1
        self.pairing_df = temp1.append(temp2)

        # Use TargetEncoder to encode the flight Origin and Destination
        encoder = TargetEncoder()
        self.pairing_df['Origin'] = encoder.fit_transform(
            self.pairing_df['Origin'], self.pairing_df['cost'])
        encoder = TargetEncoder()
        self.pairing_df['Dest'] = encoder.fit_transform(
            self.pairing_df['Dest'], self.pairing_df['cost'])
        encoder = TargetEncoder()
        self.pairing_df['Tail_Number'] = encoder.fit_transform(
            self.pairing_df['Tail_Number'], self.pairing_df['cost'])

        # print column name with total nan values in it
        nan_col_count = self.pairing_df.isna().sum()
        logging.info("Number of NA values for each feature")
        logging.info(nan_col_count)

    def plot_histogram(self):
        '''
        Plot histogram graph for the pairing feature

        Returns
        -------
        None.

        '''
        self.pairing_df['cost'].plot.hist(title="Flight Cost Distribution")
        plt.xlabel('Cost')
        plt.ylabel('# of occurance')
        plt.show()

    def calculate_Correlations(self):
        '''
        Default it uses Pearson corralation coefficient that goes from -1 to 1


        Returns
        -------
        None.

        '''

        correlations = self.pairing_df.corr()
        plt.figure(figsize=(12, 10))
        sns.heatmap(correlations, annot=True, cmap=plt.cm.Reds)
        correlations = correlations['cost']
        logging.info(correlations)

    def plot_scatter(self, feature):
        '''
        plot passed-in feature with the target "cost" to visualize the corralation

        Parameters
        ----------
        feature : TYPE
            DESCRIPTION.

        Returns
        -------
        None.

        '''
        # plot each feature with the target "cost" to visualize the corralation
        self.pairing_df.plot.scatter(x=feature, y='cost')
        plt.show()

    def plot_pivot(self, feature):
        '''
        plot pivot for the passed-in feature

        Parameters
        ----------
        feature : TYPE
            DESCRIPTION.

        Returns
        -------
        None.

        '''
        # Pivot plot shows the relationship between two features or a feature/target
        pivot = pd.pivot_table(self.pairing_df.sample(
            10), values='cost', index=[feature], aggfunc=np.mean)
        pivot.plot(kind='bar')
        plt.show()

    def plot_pair(self, feature):
        '''
        pairplot gives histogram of all the numerical features along the diagonal and shows the
        graph between two features

        Parameters
        ----------
        feature : TYPE
            DESCRIPTION.

        Returns
        -------
        None.

        '''
        sns.set_style("whitegrid")
        # sns.pairplot(abs(self.pairing_df.sample(1000)),size=3)
        sns.pairplot(self.pairing_df.sample(1000), hue=feature, size=3)
        sns.boxplot(x=feature, y='cost', data=self.pairing_df.sample(10))
        plt.show()

    def plot_join_plot(self, feature, target):
        '''
        Plot join graph for the passed in feature and target variable

        Parameters
        ----------
        feature : TYPE
            DESCRIPTION.
        target : TYPE
            DESCRIPTION.

        Returns
        -------
        None.

        '''
        j = sns.jointplot(feature, target, data=self.pairing_df, kind='reg')
        j.annotate(stats.pearsonr)
        plt.show()


'''
gf=GenericFeature()
flight_df=gf.load()
flight_df.to_csv("flights.csv")
'''

flight_df = pd.read_csv("flights.csv")
flight_df['FL_DATE'] = pd.to_datetime(flight_df['FL_DATE'])
flight_df = flight_df.sample(100)
nan_val = flight_df.isnull().values.any()
flight_df = flight_df.fillna(0)
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
# sns.relplot(data=flight_df, x="DISTANCE", y="TAIL_NUM", row="DEST", hue="ORIGIN", col="AIR_TIME") #hangs
# sns.relplot(data=flight_df, kind="line") #only numeric/date
#sns.scatterplot(data=flight_df, x="FL_DATE", y="DISTANCE", style="DEST", hue="CRS_DEP_TIME")
# sns.lineplot(data=flight_df, x="FL_DATE", y="DISTANCE", style="DEST", hue="CRS_DEP_TIME") good one
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
# sns.kdeplot(data=flight_df)
# sns.kdeplot(data=flight_df,x="DISTANCE")
#sns.kdeplot(data=flight_df,x="DISTANCE", y="FL_DATE")

# sns.rugplot(data=flight_df)
# sns.rugplot(data=flight_df,x="DISTANCE")

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
g = sns.regplot(x="CRS_DEP_TIME", y="DISTANCE", data=flight_df,
                color="r", marker="+", x_estimator=np.mean)


'''
flight_df=flight_df.drop(["FL_DATE","MKT_UNIQUE_CARRIER","TAIL_NUM","DEST","ORIGIN"], axis=1, inplace=True)
'''
