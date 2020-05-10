import numpy as np
import pandas as pd

categories = pd.read_csv('../data/categories.csv')
#from sklearn.model_selection import train_test_split
#import tqdm

'''
Для пользователя у нас есть один товар реальный
K предсказанных
хотим метрику, которая говорит, что круто, если среди предсказанных товаров есть реальный
'''

def mnap_k(predictions, target, k=20):
    U = len(predictions)
    summ = 0
    for i in range(U):
        tar = target[i]
        pr = predictions[i]
        k1 = min(k, len(tar))
        ru = list(map(lambda x: float(int(x in tar)), pr[:k]))
        pu = []
        for j in range(k):
            pu.append(sum(ru[:(j + 1)]) / (j + 1))
            
        summ += sum(np.asarray(pu) * np.asarray(ru)) / k1
        
    return summ / U
	
'''
на сколько далеко выдаваемые категории находятся друг от друга
 в дереве категорий Yandex market
 (либо озона, пока - озон)
'''
def category_distance(category1, category2):
    if (category1 == category2):
        return 0
    BU_Level3_category1 = categories.loc[categories['BU_Level4'] == category1].iloc[0]['BU_Level3']
    BU_Level3_category2 = categories.loc[categories['BU_Level4'] == category2].iloc[0]['BU_Level3']
    if (BU_Level3_category1 == BU_Level3_category2):
        return 1
    
    BU_Level2_category1 = categories.loc[categories['BU_Level4'] == category1].iloc[0]['BU_Level2']
    BU_Level2_category2 = categories.loc[categories['BU_Level4'] == category2].iloc[0]['BU_Level2']
    if (BU_Level3_category1 == BU_Level3_category2):
        return 2
    
    BU_Level1_category1 = categories.loc[categories['BU_Level4'] == category1].iloc[0]['BU_Level1']
    BU_Level1_category2 = categories.loc[categories['BU_Level4'] == category2].iloc[0]['BU_Level1']
    if (BU_Level1_category1 == BU_Level1_category2):
        return 3
    return 4
	
def diversiry(predictions):
	l = len(predictions)
	distance = 0
	for prediction in predictions:
		for i in range(len(prediction)):
			for j in range(i + 1, len(prediction)):
				dictance += category_distance(prediction[i], prediction[j])
	return distance / l
	