from sklearn.multiclass import OneVsRestClassifier
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import roc_auc_score
import pandas as pd
import numpy as np
#from metrics import hitrate
from models.metrics import hitrate
from sklearn.model_selection import train_test_split
from models.product import getTopInCategory
hobby = ['Чтение', 'Фотография', 'Кулинария', 'Спорт', 'Настольные игры', 'Кино', 'Музыка', 
         'Видеоигры', 'IT', 'Футбол', 'Цветоводство', 'Рукоделие', 'Видеомонтаж', 'Бокс', 'Туризм', 'Рисование']

holiday = ['День рождения', 'Новый год', '23 февраля', '8 марта', 'Годовщина отношений', 'День Святого Валентина', 'Вне праздника']

#social_connection = ['Друг', 'Коллега', 'Парень/девушка', 'Мать/Отец', 'Родственник']
#category = ['man', 'woman']
#numeric = ['age']
columns = hobby + holiday# + category# + numeric #+ social_connection 

class baseline():
	def __init__(self, max_cost, min_cost = 0, k = 5, n = 1):
		self.model = RandomForestClassifier()#criterion = ''
		self.categories = []
		self.criterion = {}
		self.k = k
		self.min_cost = min_cost
		self.max_cost = max_cost
		
		df_unique = pd.read_csv('C:/Users/msson/machine learning/курсовая/data/training_sample_unique.csv')#, sep=';',encoding='cp1251')
		self.categories = pd.read_csv('C:/Users/msson/machine learning/курсовая/data/categories_with_yandex.csv')
		df_unique = df_unique.sample(frac=1)
		
		self.df_unique = df_unique

	def predict(self, X_test, hobby):
		return np.asarray(self.model.predict_proba(X_test))[:, :, 1].T
	
	def get_first_k(self, pred):
		ind = len(self.categories) - self.k
		return np.array([np.partition(pred[i], ind)[ind] for i in range(len(pred))])
		
	def get_categories(self, X_test):
		ans = []
		for ind, row in X_test.iterrows():
    
			suitable_set = self.df_unique.loc[self.df_unique['age'] < row.age + 2].loc[self.df_unique['age'] > row.age - 2]
			test = suitable_set
			for i in row.index.values:
				if (row[i] == 0):
					test = test.loc[test[i] == 0]
			if (test.shape[0] > self.k):
				test['sum'] = test[columns].sum(axis = 1)
				test = test.loc[test['sum'] > 0]
			ans.append([test[:self.k]['BU_Level4'].values])
		return ans
		
		
	def get_gifts(self, X_test):
		df = self.get_categories(X_test)
		gifts = pd.DataFrame()
		for i in df[0][0]:
			a = np.asarray(self.categories.loc[self.categories['BU_Level4'] == i].yandex_category_id)[0]

			try:
				if (gifts.shape[0] != 0):
					b = getTopInCategory(1, int(a), 1000, min_price=0, page=1) 
					gifts = pd.concat([gifts, b], axis=0)
				else:
					gifts = getTopInCategory(1, int(a), 1000, min_price=0, page=1)
				#arr0 = np.append(arr0, a)
			except:
				continue
		return gifts