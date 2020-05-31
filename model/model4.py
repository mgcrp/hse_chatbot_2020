# -------------------- ИМПОРТЫ --------------------

import os
import sys

sys.path.append("..")
os.chdir("..")

import pickle

import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.multiclass import OneVsRestClassifier
from xgboost import XGBClassifier
from sklearn.preprocessing import MultiLabelBinarizer

from model.product import getTopInCategory

# -------------------- ГЛОБАЛЬНЫЕ ПЕРЕМЕННЫЕ/КОНСТАНТЫ --------------------

FILENAME = 'model/model4_saved.sav'

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

        df = pd.read_csv('data/training_sample_xgboost.csv')
        self.categories = df.columns[26:]

    def predict(self, X_test):
        return self.model.predict_proba(X_test)

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
            a = i
            try:
                if (gifts.shape[0] != 0):
                    b = getTopInCategory(self.n, int(a), max_cost, min_price=min_cost, page=1)
                    b['cat_id'] = int(float(a))
                    gifts = pd.concat([gifts, b], axis=0)
                else:
                    gifts = getTopInCategory(self.n, int(a), max_cost, min_price=min_cost, page=1)
                    gifts['cat_id'] = int(float(a))
            except:
                continue
        return gifts


def get_gifts(X_test, hobby=[], max_cost=10000, min_cost=0):
    loaded_model = pickle.load(open(FILENAME, 'rb'))
    model = model1(loaded_model)
    return list(model.get_gifts_(X_test, hobby, max_cost, min_cost).apply(lambda x: {'model':x.id, 'category':x.cat_id}, axis=1))


def learn_model1():
    model = OneVsRestClassifier(XGBClassifier(n_jobs=-1, max_depth=4))

    df = pd.read_csv('data/training_sample_xgboost.csv')
    df = df.sample(frac=1)

    X_train = df[df.columns[:26]]
    y_train = df[df.columns[26:]]

    X_train = df.drop(['BU_Level4', 'name', 'cat_ya_id', 'cat_ya'], axis=1)

    model.fit(X_train, y_train)
    pickle.dump(model, open(FILENAME, 'wb'))
