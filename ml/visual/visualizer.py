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
import crewml.exception as exp
import matplotlib.pyplot as plt


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

        self.fig=None
        self.axes_subplot =None
        self.x = 10
        self.y = 10
        self.titles = None
        self.total_plots = 1
        self.total_figures = 1

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

    def set_total_plots(self, total_plots):
        '''
        Set the total plots to plot

        Parameters
        ----------
        total_plots : numeric
            DESCRIPTION.

        Returns
        -------
        None.

        '''

        self.total_plots = total_plots
        self.fig, self.axes_subplot = plt.subplots(
            nrows=self.total_plots, ncols=self.total_plots)
        self.fig.tight_layout()
        plt.xticks(fontsize=2)
        plt.yticks(fontsize=2)
        plt.legend(fontsize='small', title_fontsize='5')
        plt.show()

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

        num_list = self.feature.get_numeric_x_y()
        tot_num_list=len(num_list)
        if tot_num_list> 16:
            raise exp.CrewmlAttributeError(
                "Total Number of Numeric features exceeded 16:"+num_list)

        # This will create 4X4 matrix of Figure and AxesSubPlot objects
        # that can be used to plot maximum of 16 graphs in one figure.
        self.set_total_plots(4)
        self.fig.suptitle(self.name+"-Two feature Plot-" +plot_type, fontsize=20)
        data = self.feature.all_features()
        k = 0
        for i in range(4):
            for j in range(4):
                num_x_y = num_list[k]
                print("i=, j=, k=", i, j, k)
                if plot_type == "scatter":
                    sns.scatterplot(
                        ax=self.axes_subplot[i][j], data=data, x=num_x_y[0],
                        y=num_x_y[1], hue=hue)
                else:
                    sns.lineplot(
                        ax=self.axes_subplot[i][j], data=data, x=num_x_y[0],
                        y=num_x_y[1], hue=hue)
                self.axes_subplot[i][j].set_xlabel(num_x_y[0], fontsize=7)
                self.axes_subplot[i][j].set_ylabel(num_x_y[1], fontsize=7)
                k += 1
                if k == tot_num_list:
                    return

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
        cat_feat_names=self.feature.categorical_feature_names()
        for cat in cat_feat_names:
            self.plot_numeric_features(plot_type,hue=cat)
        

class DistributionPlot(Visualizer):
    def __init__(self):
        super().__init__()


class CategorialPlot(Visualizer):
    def __init__(self):
        super().__init__()


class RegressionPlot(Visualizer):
    def __init__(self):
        super().__init__()
