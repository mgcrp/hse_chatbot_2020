from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import roc_auc_score
import pandas as pd
import numpy as np
#from metrics import hitrate
from models.metrics import hitrate
from sklearn.model_selection import train_test_split

class model1():
	def __init__(self, k = 5):
		self.model = RandomForestClassifier()#criterion = ''
		self.categories = []
		self.criterion = {}
		self.k = k
		
		df = pd.read_csv('C:/Users/msson/machine learning/курсовая/data/training_sample.csv')#, sep=';',encoding='cp1251')
		
		df = df.sample(frac=1)
		df = df[:1000]
		
		y_train = df.BU_Level4
		self.categories = y_train.unique()
		y_train = pd.get_dummies(y_train)

		X_train = df.drop(['BU_Level4', 'ItemEAN'], axis = 1)
		#print(df)
		self.model.fit(X_train, y_train)
		
		X_train, X_test, y_train, y_test = train_test_split(X_train, y_train, test_size=0.2, random_state=42)
		pred = self.predict(X_test)
		cat = self.get_categories(X_test)
		self.criterion['hitrate'] = metrics.hitrate(pred, np.asarray(y_test))
		self.criterion['diversity'] = metrics.diversity(cat)
		

	def predict(self, X_test):
		return np.asarray(self.model.predict_proba(X_test))[:, :, 1].T
	
	def get_first_k(self, pred):
		ind = len(self.categories) - self.k
		return np.array([np.partition(pred[i], ind)[ind] for i in range(len(pred))])
		
	def get_categories(self, X_test):		
		pred = self.predict(X_test)
		
		first_k = self.get_first_k(pred)
		for i in range(first_k.shape[0]):
			kk = max(first_k[i], 0.0001)
			pred[i][pred[i] >= kk] = 1
			pred[i][pred[i] < kk] = 0
		
		pred = np.array(pred, dtype = int)
		pred = np.array(pred, dtype = bool)
		c = np.array([ np.asarray(self.categories) for i in range(pred.shape[0]) ])
		out = np.array([ c[i, pred[i]] for i in range(pred.shape[0]) ])

		return out
		
		