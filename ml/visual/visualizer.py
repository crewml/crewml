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
    fig_styles=["white_grid", "dark_grid", "white", "dark", "ticks"] 
    fig_contexts=["paper", "notebook", "talk", "poster"]
    
    def __init__(self, fig_style=None, fig_context=None):
        self.logger = logging.getLogger(__name__)
        if fig_style == None:
            self.fig_style=Visualizer.fig_styles[2]
        elif fig_style not in str(Visualizer.fig_styles):
            raise exp.CrewmlAttributeError("Invalid filg_style passed:"+fig_style)
        else:
            self.fig_style=fig_style
            
        if fig_context == None:
            self.fig_context=Visualizer.fig_contexts[2]
        elif fig_context not in str(Visualizer.fig_contexts):
            raise exp.CrewmlAttributeError("Invalid filg_style passed:"+fig_context)
        else:
            self.fig_style=fig_style      
            
        self.fig, self.axes_subplot = plt.subplots(nrows=1, ncols=1)
        self.x=10
        self.y=10
        self.titles=None
        self.total_plots=1
        self.total_figures=1
        self.x_labels=None
        self.y_lables=None
        
                         
    def set_fig_style(self,fig_style):
        self.fig_style=fig_style

    def set_fig_context(self,fig_style):
        self.fig_style=fig_style
                        
    def set_range(self,x,y):
        self.x=x
        self.y=y
        
    def set_total_plots(self,total_plots):
        self.total_plots=total_plots
        self.fig, self.axes_subplot = plt.subplots(nrows=self.total_plots, ncols=self.total_plots)
        self.fig.tight_layout() 
        plt.xticks(fontsize= 2)
        plt.yticks(fontsize= 2)
        plt.show()
 
   

    def set_titles(self,titles):
        if len(titles) != self.total_plots :
            raise exp.CrewmlValueError("total number of titles must to equal to \
                total_plots:total_plots")
        
    def set_xlabels(self,x_labels):   
       self.x_labels=x_labels


class RelationalPlot(Visualizer):
    types=["scatter","line"]
    def __init__(self, feature):
        self.feature=feature
        self.type=None
        self.name=self.feature.get_feature_name()

        
    def plot_numeric_features(self, type):
        if type not in str(RelationalPlot.types):
            raise exp.CrewmlAttributeError("Invalid RelationalPlot type passed:"+type)
            
        num_list=self.feature.get_numeric_x_y()
        if len(num_list) > 16:
            raise exp.CrewmlAttributeError("Total Number of Numeric features exceeded 12:"+num_list)

        
        
        #This will create 4X4 matrix of Figure and AxesSubPlot objects that can be used
        #to plot maximum of 16 graphs in one figure. 
        self.set_total_plots(4)
        self.fig.suptitle(self.name+"-Two feature Scatter Plot", fontsize=20) 
        data=self.feature.all_features()
        k=0        
        for i in range(4):           
            for j in range(4):
                num_x_y=num_list[k]
                print("i=, j=, k=",i,j,k)
                sns.scatterplot(ax=self.axes_subplot[i][j],data=data, x=num_x_y[0], y=num_x_y[1])
                self.axes_subplot[i][j].set_xlabel(num_x_y[0], fontsize=7)
                self.axes_subplot[i][j].set_ylabel(num_x_y[1], fontsize=7)
                k+=1
                if k== 10:
                    return
            
            

        
    
class DistributionPlot(Visualizer):
    def __init__(self):
        pass
    
class CategorialPlot(Visualizer):
    def __init__(self):
        pass

class RegressionPlot(Visualizer):
    def __init__(self):
        pass