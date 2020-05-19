# -------------------- ИМПОРТЫ --------------------

import pickle

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import train_test_split

# from metrics import hitrate
from models.metrics import hitrate
from models.product import getTopInCategory

# -------------------- ГЛОБАЛЬНЫЕ ПЕРЕМЕННЫЕ/КОНСТАНТЫ --------------------

FILENAME = 'data/finalized_model.sav'

# -------------------- КЛАССЫ/ФУНКЦИИ --------------------


class model1():
    def __init__(self, load_model, k=5, n=1):
        self.model = load_model
        self.categories_ya = []
        self.categories = []
        self.criterion = {}
        self.k = k
        self.n = n

        self.categories_ya = pd.read_csv('data/categories_with_yandex.csv')

        df = pd.read_csv('data/training_sample.csv')
        y_train = df.BU_Level4
        self.categories = y_train.unique()

        #X_train, X_test, y_train, y_test = train_test_split(X_train, y_train, test_size=0.2, random_state=42)
        #pred = self.predict(X_test)
        #cat = self.get_categories(X_test)
        #self.criterion['hitrate'] = hitrate(pred, np.asarray(y_test))
        #self.criterion['diversity'] = diversity(cat)

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

        pred = np.array(pred, dtype=int)
        pred = np.array(pred, dtype=bool)
        c = np.array([np.asarray(self.categories) for i in range(pred.shape[0])])
        out = np.array([c[i, pred[i]] for i in range(pred.shape[0])])

        return out

    def get_gifts_(self, X_test, hobby=[], max_cost=10000, min_cost=0):
        df = self.get_categories(X_test)
        gifts = pd.DataFrame()
        for i in df[0]:
            a = np.asarray(self.categories_ya.loc[self.categories_ya['BU_Level4'] == i].yandex_category_id)[0]

            try:
                if (gifts.shape[0] != 0):
                    b = getTopInCategory(self.n, int(a), max_cost, min_price=min_cost, page=1)
                    gifts = pd.concat([gifts, b], axis=0)
                else:
                    gifts = getTopInCategory(self.n, int(a), max_cost, min_price=min_cost, page=1)
            except:
                continue
        return gifts


def get_gifts(X_test, hobby=[], max_cost=10000, min_cost=0):
    loaded_model = pickle.load(open(FILENAME, 'rb'))
    model = model1(loaded_model)
    return model.get_gifts_(X_test, hobby, max_cost, min_cost)


def learn_model1():
    model = RandomForestClassifier()

    df = pd.read_csv('data/training_sample.csv')
    df = df.sample(frac=1)
    #df = df[:1000]

    y_train = df.BU_Level4
    y_train = pd.get_dummies(y_train)

    X_train = df.drop(['BU_Level4', 'ItemEAN', 'cat_ya_id', 'cat_ya'], axis=1)

    model.fit(X_train, y_train)
    pickle.dump(model, open(FILENAME, 'wb'))
