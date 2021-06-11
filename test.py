import crewml.data.feature as fet
import crewml.visual.visualizer as vis

import itertools
import logging.config
import pandas as pd
import numpy as np
import datetime as dt

import crewml.common as st

logging.config.fileConfig(st.RESOURCE_DIR+'logging.ini',
                          disable_existing_loggers=False)

'''
feature = fet.Feature()
feature.load()
feature_names = feature.all_feature_names()
feature_names_combo = list(itertools.combinations(feature_names, 3))

cp = vis.MultiPlot(feature)
cp.plot(plot_type="joint", hue=True)

'''

# example of training a final classification model
from sklearn.linear_model import LogisticRegression
from sklearn.datasets import make_blobs
from sklearn.metrics import accuracy_score
# generate 2d classification dataset
X, y = make_blobs(n_samples=100, centers=10, n_features=20, random_state=1)
# fit final model
model = LogisticRegression()
model.fit(X, y)
# new instances where we do not know the answer
Xnew, ynew = make_blobs(n_samples=30, centers=10, n_features=20, random_state=1)
# make a prediction
ynew_predict = model.predict(Xnew)


    
accuracy = accuracy_score(ynew, ynew_predict)
print("Accuracy: %.2f%%" % (accuracy * 100.0))    