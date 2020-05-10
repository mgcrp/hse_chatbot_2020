from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import roc_auc_score
import pandas as pd
import numpy as np

class model1():
	def __init__(self):
		self.model = RandomForestClassifier()
		self.categories = []
		
		df = pd.read_csv('data/training_sample.csv')#, sep=';',encoding='cp1251')
		
		df = df.sample(frac=1)
		df = df[:10000]
		
		y_train = df.BU_Level4
		self.categories = y_train.unique()
		y_train = pd.get_dummies(y_train)

		X_train = df.drop(['BU_Level4', 'ItemEAN'], axis = 1)
		self.model.fit(X_train, y_train)


	def predict(self, X_test):
		dff = pd.DataFrame()
		dff['cat'] = self.categories
		dff['pred'] = np.asarray(self.model.predict_proba(X_test))[:,0][:,1]
		dff = dff.loc[dff['pred'] > 0.01]
		return dff
	
        #return self.model.predict(X_test)