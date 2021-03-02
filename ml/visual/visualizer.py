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
import seaborn as sns
import numpy as np
import crewml.exception as exp
import matplotlib.pyplot as plt
import itertools
import pandas as pd


class Visualizer:
    '''
    Parent class for all visualization classes. It contains all the basic
    matlab plot objects like Figure, Axes to generically create the subplot
    and figure objects for the subclasses use it to plot the features
    '''
    fig_styles = ["white_grid", "dark_grid", "white", "dark", "ticks"]
    fig_contexts = ["paper", "notebook", "talk", "poster"]

    def __init__(self, fig_style=None, fig_context=None):
        '''
        Create Visualizer with default Figure and Axies objects

        Parameters
        ----------
        fig_style : TYPE, optional
            DESCRIPTION. The default is None.
        fig_context : TYPE, optional
            DESCRIPTION. The default is None.

        Raises
        ------
        exp
            DESCRIPTION.

        Returns
        -------
        None.

        '''
        self.logger = logging.getLogger(__name__)
        if fig_style is None:
            self.fig_style = Visualizer.fig_styles[2]
        elif fig_style not in str(Visualizer.fig_styles):
            raise exp.CrewmlAttributeError(
                "Invalid filg_style passed:"+fig_style)
        else:
            self.fig_style = fig_style

        if fig_context is None:
            self.fig_context = Visualizer.fig_contexts[2]
        elif fig_context not in str(Visualizer.fig_contexts):
            raise exp.CrewmlAttributeError(
                "Invalid filg_style passed:"+fig_context)
        else:
            self.fig_style = fig_style

    def set_fig_style(self, fig_style):
        '''
         Set one of the values: white_grid", "dark_grid", "white", "dark",
         "ticks"

        Parameters
        ----------
        fig_style : str
            DESCRIPTION.

        Raises
        ------
        exp
            CrewmlAttributeError.

        Returns
        -------
        None.

        '''
        if fig_style not in str(Visualizer.fig_styles):
            raise exp.CrewmlAttributeError(
                "Invalid filg_style passed:"+fig_style)
        self.fig_style = fig_style

    def set_fig_context(self, fig_context):
        '''
        set the figure context "paper", "notebook", "talk", "poster"

        Parameters
        ----------
        fig_context : str
            DESCRIPTION.

        Raises
        ------
        exp
            CrewmlAttributeError.

        Returns
        -------
        None.

        '''

        if fig_context not in str(Visualizer.fig_contexts):
            raise exp.CrewmlAttributeError(
                "Invalid filg_style passed:"+fig_context)
        self.fig_context = fig_context

    def set_range(self, x, y):
        '''
        Parameters
        ----------
        x : TYPE
            DESCRIPTION.
        y : TYPE
            DESCRIPTION.

        Returns
        -------
        None.

        '''
        self.x = x
        self.y = y

    def set_total_plots(self, total_plots, total_columns):
        # Compute Rows required
        rows = total_plots // total_columns
        rows += total_plots % total_columns

        # Create a Position index
        position = range(1, total_plots + 1)
        self.axes_subplot = []
        # Create main figure
        self.fig = plt.figure(1)
        self.fig.tight_layout()
        # plt.legend(fontsize='small', title_fontsize='5')
        # self.fig.subplots_adjust(hspace=2)
        # self.fig.subplots_adjust(wspace=1)

        for k in range(total_plots):
            # add every single subplot to the figure with a for loop
            ax = self.fig.add_subplot(rows, total_columns, position[k])
            self.axes_subplot.append(ax)

        # plt.legend(fontsize='small', title_fontsize='5')

    def set_titles(self, titles):
        '''
        Parameters
        ----------
        titles : TYPE
            DESCRIPTION.

        Raises
        ------
        exp
            DESCRIPTION.

        Returns
        -------
        None.

        '''
        if len(titles) != self.total_plots:
            raise exp.CrewmlValueError("total number of titles must to \
                        equal to total_plots:total_plots")

    def set_xlabels(self, x_labels):
        '''
        Parameters
        ----------
        x_labels : TYPE
            DESCRIPTION.

        Returns
        -------
        None.

        '''
        self.x_labels = x_labels


class RelationalPlot(Visualizer):
    '''
     This class extends Visualizer and has functions to draw Seaborn Relational
     plots by taking the features from the Feature object. It plots
     maximum of 16 plots in one Figure object mostly using default font
     and color.It is mainly used to visualize the relationship between
     two numerical features or two numerical features with a third
     categorical featuer
    '''
    plot_types = ["scatter", "line"]

    def __init__(self, feature, fig_style=None, fig_context=None):
        '''
        Create RelationalPlot with Feature object

        Parameters
        ----------
        feature : Feature
            Featiure object.

        Returns
        -------
        None.

        '''
        self.feature = feature
        self.type = None
        self.name = self.feature.get_feature_name()
        super().__init__()

    def plot_numeric_features(self, plot_type, hue=None):
        '''
        This function plots numeric features

        Parameters
        ----------
        plot_type : str
            "scatter", "line"

        Raises
        ------
        exp
            CrewmlAttributeError.

        Returns
        -------
        None.

        '''

        if plot_type not in str(RelationalPlot.plot_types):
            raise exp.CrewmlAttributeError(
                "Invalid RelationalPlot type passed:"+plot_type)

        data = self.feature.all_features()
        num_x_y = self.feature.get_numeric_x_y()
        num_list_tot = len(num_x_y)

        # total num_list_tot plots with 3 columns in one figure
        self.set_total_plots(num_list_tot, 3)
        self.fig.suptitle(self.name+"-Two feature Plot-" +
                          plot_type, fontsize=20)

        for i in range(num_list_tot):
            self.axes_subplot[i].set_xlabel(num_x_y[i][0], fontsize=5)
            self.axes_subplot[i].set_ylabel(num_x_y[i][1], fontsize=5)
            if plot_type == "scatter":
                sns.scatterplot(
                    ax=self.axes_subplot[i], data=data, x=num_x_y[i][0],
                    y=num_x_y[i][1], hue=hue)

            else:
                sns.lineplot(
                    ax=self.axes_subplot[i], data=data, x=num_x_y[i][0],
                    y=num_x_y[i][1], hue=hue)

    def plot_num_cat_features(self, plot_type):
        '''
        This function uses the plot_numeric_features to plot all the numeric
        features with categorical features. Each Category along with numeric
        features plotted in a seperate Figure object

        Parameters
        ----------
        plot_type : TYPE
            DESCRIPTION.

        Returns
        -------
        None.

        '''
        cat_feat_names = self.feature.categorical_feature_names()
        for cat in cat_feat_names:
            self.plot_numeric_features(plot_type, hue=cat)


class DistributionPlot(Visualizer):
    plot_types = ["hist", "kde", "ecdf", "rug"]

    def __init__(self, feature):
        super().__init__()

        self.feature = feature
        self.name = self.feature.get_feature_name()

    def plot_numeric_univariate(self, plot_type, hue=None):
        if plot_type not in str(DistributionPlot.plot_types):
            raise exp.CrewmlAttributeError(
                "Invalid DistributionPlot type passed:"+plot_type)
        num_features = self.feature.numeric_feature_names()
        num_list_tot = len(num_features)

        # total num_list_tot plots with 3 columns in one figure
        self.set_total_plots(num_list_tot, 3)
        self.fig.suptitle(self.name+"-One feature Plot-" +
                          plot_type, fontsize=20)
        data = self.feature.all_features()

        for i in range(num_list_tot):
            if plot_type == "hist":
                sns.histplot(
                    ax=self.axes_subplot[i], data=data, x=num_features[i],
                    hue=hue)
            elif plot_type == "kde":
                sns.kdeplot(
                    ax=self.axes_subplot[i], data=data, x=num_features[i],
                    hue=hue)
            elif plot_type == "ecdf":
                sns.ecdfplot(
                    ax=self.axes_subplot[i], data=data, x=num_features[i],
                    hue=hue)
            elif plot_type == "rug":
                sns.rugplot(
                    ax=self.axes_subplot[i], data=data, x=num_features[i],
                    hue=hue)
            self.axes_subplot[i].set_xlabel(num_features[i], fontsize=7)
            self.axes_subplot[i].set_ylabel(num_features[i], fontsize=7)

    def plot_numeric_bivariate(self, plot_type, hue=None):
        if plot_type not in str(DistributionPlot.plot_types):
            raise exp.CrewmlAttributeError(
                "Invalid DistributionPlot type passed:"+plot_type)
        num_features = self.feature.get_numeric_x_y()
        num_list_tot = len(num_features)

        # total num_list_tot plots with 3 columns in one figure
        self.set_total_plots(num_list_tot, 3)
        self.fig.suptitle(self.name+"-One feature Plot-" +
                          plot_type, fontsize=20)
        data = self.feature.all_features()

        for i in range(num_list_tot):
            if plot_type == "hist":
                sns.histplot(
                    ax=self.axes_subplot[i], data=data, x=num_features[i][0],
                    y=num_features[i][1], hue=hue)
            elif plot_type == "kde":
                sns.kdeplot(
                    ax=self.axes_subplot[i], data=data, x=num_features[i][0],
                    y=num_features[i][1], hue=hue)
            elif plot_type == "ecdf":
                sns.ecdfplot(
                    ax=self.axes_subplot[i], data=data, x=num_features[i][0],
                    y=num_features[i][1], hue=hue)
            elif plot_type == "rug":
                sns.rugplot(
                    ax=self.axes_subplot[i], data=data, x=num_features[i][0],
                    y=num_features[i][1], hue=hue)
            self.axes_subplot[i].set_xlabel(num_features[i], fontsize=7)
            self.axes_subplot[i].set_ylabel(num_features[i], fontsize=7)


class CategorialPlot(Visualizer):
    scatter_plot_type = ["strip", "swarm",
                         "box", "violin", "point", "bar", "count"]

    def __init__(self, feature, sample=True):
        self.feature = feature
        self.name = self.feature.get_feature_name()
        self.sample = sample
        super().__init__()

    # stripplot swarmplot
    def plot_univariate(self, plot_type):
        if plot_type not in str(CategorialPlot.scatter_plot_type):
            raise exp.CrewmlAttributeError(
                "Invalid CategorialPlot type passed:"+plot_type)

        if plot_type == CategorialPlot.scatter_plot_type[6]:
            feature_names = self.feature.categorical_feature_names()
            data = self.feature.categorical_features()
        else:
            feature_names = self.feature.numeric_feature_names()
            data = self.feature.numeric_features()
            data = data.apply(pd.to_numeric)
        tot_plots = len(feature_names)

        if tot_plots > self.feature.get_max_plots():
            print("total plots exceeded allowable max \
                  plots: total_plots and max_plots",
                  tot_plots, self.feature.get_max_plots())
            tot_plots = self.feature.get_max_plots()

        # total tot_plots, with 3 columns in one figure
        self.set_total_plots(tot_plots, 3)
        if self.sample is True:
            data = data.sample(1000)

        for i in range(tot_plots):
            if plot_type == CategorialPlot.scatter_plot_type[0]:
                sns.stripplot(data=data,
                              ax=self.axes_subplot[i],
                              x=feature_names[i])
            elif plot_type == CategorialPlot.scatter_plot_type[1]:
                sns.swarmplot(data=data,
                              ax=self.axes_subplot[i],
                              x=feature_names[i])
            elif plot_type == CategorialPlot.scatter_plot_type[2]:
                sns.boxplot(data=data,
                            ax=self.axes_subplot[i],
                            x=feature_names[i])
            elif plot_type == CategorialPlot.scatter_plot_type[3]:
                sns.violinplot(data=data,
                               ax=self.axes_subplot[i],
                               x=feature_names[i])
            elif plot_type == CategorialPlot.scatter_plot_type[4]:
                sns.pointplot(data=data,
                              ax=self.axes_subplot[i],
                              x=feature_names[i])
            elif plot_type == CategorialPlot.scatter_plot_type[5]:
                sns.barplot(data=data,
                            ax=self.axes_subplot[i],
                            x=feature_names[i])
            elif plot_type == CategorialPlot.scatter_plot_type[6]:
                sns.countplot(data=data,
                              ax=self.axes_subplot[i],
                              x=feature_names[i])

    def plot_bivariate(self, plot_type, hue=False):
        if plot_type not in str(CategorialPlot.scatter_plot_type):
            raise exp.CrewmlAttributeError(
                "Invalid CategorialPlot type passed:"+plot_type)

        num_feature_names = self.feature.numeric_feature_names()
        cat_feature_names = self.feature.categorical_feature_names()

        feature_names = list(itertools.combinations(num_feature_names, 2))
        tot_plots = len(feature_names)

        if tot_plots > self.feature.get_max_plots():
            print("total plots exceeded allowable max plots:\
                  total_plots and max_plots",
                  tot_plots, self.feature.get_max_plots())
        tot_plots = self.feature.get_max_plots()

        # total tot_plots, with 3 columns in one figure
        self.set_total_plots(tot_plots, 3)
        data = self.feature.all_features()
        if self.sample is True:
            data = data.sample(100)
        # relace all NA column values with 0 string value
        data = data.replace(np.nan, '0', regex=True)
        data = data.astype(str)

        for i in range(tot_plots):
            if hue is False:
                if plot_type == CategorialPlot.scatter_plot_type[0]:
                    sns.stripplot(data=data,
                                  ax=self.axes_subplot[i],
                                  x=feature_names[i][0],
                                  y=data[feature_names[i][1]])
                elif plot_type == CategorialPlot.scatter_plot_type[1]:
                    sns.swarmplot(data=data,
                                  ax=self.axes_subplot[i],
                                  x=feature_names[i][0],
                                  y=feature_names[i][1])
                elif plot_type == CategorialPlot.scatter_plot_type[2]:
                    sns.boxplot(data=data,
                                ax=self.axes_subplot[i],
                                x=feature_names[i][0],
                                y=feature_names[i][1])
                elif plot_type == CategorialPlot.scatter_plot_type[3]:
                    sns.violinlot(data=data,
                                  ax=self.axes_subplot[i],
                                  x=feature_names[i][0],
                                  y=feature_names[i][1])
            else:
                for j in range(len(cat_feature_names)):
                    if plot_type == CategorialPlot.scatter_plot_type[0]:
                        sns.stripplot(data=data,
                                      ax=self.axes_subplot[i],
                                      x=feature_names[i][0],
                                      y=feature_names[i][1],
                                      hue=num_feature_names[j])
                    else:
                        sns.swarmplot(data=data,
                                      ax=self.axes_subplot[i],
                                      x=feature_names[i][0],
                                      y=feature_names[i][1],
                                      hue=num_feature_names[j])


class RegressionPlot(Visualizer):
    def __init__(self):
        super().__init__()
