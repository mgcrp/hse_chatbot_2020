# -------------------- ИМПОРТЫ --------------------

import pickle

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.neighbors import NearestNeighbors

from models.product import getTopInCategory

# -------------------- ГЛОБАЛЬНЫЕ ПЕРЕМЕННЫЕ/КОНСТАНТЫ --------------------

FILENAME = 'C:/Users/msson/machine learning/курсовая/data/knn_model.sav'

age_norm = 12

hobby = [
    'Чтение', 'Фотография', 'Кулинария', 'Спорт',
    'Настольные игры', 'Кино', 'Музыка', 'Видеоигры',
    'IT', 'Футбол', 'Цветоводство', 'Рукоделие',
    'Видеомонтаж', 'Бокс', 'Туризм'
]  # , 'Рисование']

holiday = [
    'День рождения', 'Новый год', '23 февраля', '8 марта',
    'Годовщина отношений', 'День Святого Валентина', 'Вне праздника'
]

numeric = ['age']
category = ['man', 'woman']
social_connection = ['Друг', 'Коллега', 'Парень/девушка', 'Мать/Отец', 'Родственник']

columns = hobby + holiday + category + numeric  # + social_connection

# -------------------- КЛАССЫ/ФУНКЦИИ --------------------


class model3():
    def __init__(self, load_model, k=5, n=1):
        self.model = load_model

        self.k = k
        self.n = n
        self.y_train = pd.read_csv('C:/Users/msson/machine learning/курсовая/data/model3_y_train.csv')
        self.categories_ya = pd.read_csv('C:/Users/msson/machine learning/курсовая/data/categories_with_yandex.csv')
        self.categories = pd.read_csv(
            'C:/Users/msson/machine learning/курсовая/data/model1_cats.csv')  # y_train.unique()

    def predict(self, x_pred):
        df = pd.read_csv('C:/Users/msson/machine learning/курсовая/data/training_sample_unique.csv')

        self.y_train = df.cat_ya_id

        X_train = df.drop(['BU_Level4', 'name', 'cat_ya_id', 'cat_ya'], axis=1)
        X_train1 = X_train[columns]

        X_train1['age'] = X_train1['age'] / age_norm

        x_pred = x_pred[columns]
        x_pred['age'] = x_pred['age'] / age_norm
        distances, indices = self.model.kneighbors(x_pred)

        ans = []
        for i in indices:
            for j in i:
                k = self.y_train.iloc[j]
                if (X_train1.iloc[j]['age'] < x_pred['age'].values[0] + 5 and x_pred['age'].values[0] - 5 < X_train1.iloc[j]['age']):
                    if (x_pred['age'].values[0] > 12 / age_norm):
                        if (X_train.iloc[j]['man'] == x_pred['man'].values[0]):
                            ans.append(k)
                    else:
                        ans.append(k)
        indexes = np.unique(ans, return_index=True)[1]
        ans = [ans[index] for index in sorted(indexes)]
        ans = ans[:5]
        for i in ans:
            print(i, self.categories_ya.loc[self.categories_ya['yandex_category_id']
                                            == str(int(float(i)))].head(1)['yandex_category_name'])
        return ans

    def get_gifts_(self, X_test, hobby=[], max_cost=10000, min_cost=0):
        df = self.predict(X_test)
        print(df)

        gifts = pd.DataFrame()
        for i in df:
            try:
                if (gifts.shape[0] != 0):
                    b = getTopInCategory(self.n, int(float(i)), max_cost, min_price=min_cost, page=1)
                    gifts = pd.concat([gifts, b], axis=0)
                else:
                    gifts = getTopInCategory(self.n, int(float(i)), max_cost, min_price=min_cost, page=1)
            except:
                print('bad')
                continue

        return gifts


def get_gifts(X_test, hobby=[], max_cost=10000, min_cost=0):
    loaded_model = pickle.load(open(FILENAME, 'rb'))
    model = model3(loaded_model)
    return model.get_gifts_(X_test, hobby, max_cost, min_cost)


def learn_model3():
    df = pd.read_csv('C:/Users/msson/machine learning/курсовая/data/training_sample_unique.csv')

    y_train = df.cat_ya_id

    X_train = df.drop(['BU_Level4', 'name', 'cat_ya_id', 'cat_ya'], axis=1)
    y_train.to_csv('C:/Users/msson/machine learning/курсовая/data/model3_y_train.csv', index=False)

    X_train1 = X_train[columns]

    X_train1['age'] = X_train1['age'] / age_norm

    nbrs = NearestNeighbors(n_neighbors=100, algorithm='ball_tree').fit(X_train1)
    pickle.dump(nbrs, open(FILENAME, 'wb'))
