import crewml.data.feature as fet
import crewml.visual.visualizer as vis

import itertools
import logging.config
import pandas as pd
import numpy as np

import crewml.common as st

logging.config.fileConfig(st.RESOURCE_DIR+'logging.ini',
                          disable_existing_loggers=False)

logger = logging.getLogger(__name__)
x=1 
y="test"

logger.info("this is x=%s and y=%s",x,y)

df = pd.DataFrame(data={'A': [1, 2, 3]}, 
                  index=['a', 'b', 'c'])

df_num= df['A'].tolist()
npa = np.asarray(df_num, dtype=np.int32)

labels = np.array([0, 1, 2, 3])


'''
feature = fet.Feature()
feature.load()
feature_names = feature.all_feature_names()
feature_names_combo = list(itertools.combinations(feature_names, 3))

cp = vis.MultiPlot(feature)
cp.plot(plot_type="joint", hue=True)
'''



# multiclass classification
import pandas
import xgboost
from sklearn import model_selection
from sklearn.metrics import accuracy_score
from sklearn.preprocessing import LabelEncoder
# load data
data = pandas.read_csv(st.DATA_DIR+'/raw_file/iris.csv', header=None)
dataset = data.values
# split data into X and y
X = dataset[:,0:4]
Y = dataset[:,4]
# encode string class values as integers
label_encoder = LabelEncoder()
label_encoder = label_encoder.fit(Y)
label_encoded_y = label_encoder.transform(Y)
seed = 7
test_size = 0.33
X_train, X_test, y_train, y_test = model_selection.train_test_split(X, label_encoded_y, test_size=test_size, random_state=seed)
# fit model no training data
model = xgboost.XGBClassifier()
model.fit(X_train, y_train)
print(model)
# make predictions for test data
y_pred = model.predict(X_test)
predictions = [round(value) for value in y_pred]
# evaluate predictions
accuracy = accuracy_score(y_test, predictions)
print("Accuracy: %.2f%%" % (accuracy * 100.0))
