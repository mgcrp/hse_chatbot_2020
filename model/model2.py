# -------------------- ИМПОРТЫ --------------------

import os
import sys

sys.path.append("..")
os.chdir("..")

import pickle

import numpy as np
import pandas as pd
from scipy.special import softmax
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder

import keras
import tensorflow as tf
from keras.layers import Dense

from model.product import getTopInCategory

# -------------------- ГЛОБАЛЬНЫЕ ПЕРЕМЕННЫЕ/КОНСТАНТЫ --------------------

FILENAME_MODEL = 'data/finalized_model_2.json'
FILENAME_WEIGHTS = 'data/finalized_model_2.h5'


# -------------------- КЛАССЫ/ФУНКЦИИ --------------------


class model2():
    def __init__(self, load_model, k=5, n=1):
        self.k = k
        self.n = n
        self.criterion = {}
        self.model = load_model

        self.categories_ya = pd.read_csv('data/categories_with_yandex.csv')

        df = pd.read_csv('data/training_sample_xgboost.csv').fillna(0)
        self.categories = df.columns[26:]

    def predict(self, X_test):
        return self.model.predict(X_test) / 10000000

    def get_first_k(self, pred):
        ind = len(self.categories) - self.k
        return np.array([np.partition(pred[i], ind)[ind] for i in range(len(pred))])

    def get_categories(self, X_test):
        pred = self.predict(X_test)

        first_k = self.get_first_k(pred)
        for i in range(first_k.shape[0]):
            kk = first_k[i]
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
                if gifts.shape[0] != 0:
                    b = getTopInCategory(self.n, int(a), max_cost, min_price=min_cost, page=1)
                    gifts = pd.concat([gifts, b], axis=0)
                else:
                    gifts = getTopInCategory(self.n, int(a), max_cost, min_price=min_cost, page=1)
            except:
                continue
        return gifts


def get_gifts(X_test, hobby=[], max_cost=10000, min_cost=0):
    loaded_model = pickle.load(open(FILENAME, 'rb'))
    model = model2(loaded_model)
    return model.get_gifts_(X_test, hobby, max_cost, min_cost)


def learn_model2():
    df = pd.read_csv('data/training_sample_xgboost.csv').fillna(0)

    df = df.sample(frac=1)

    y_train = df[df.columns[26:]]
    categories = df.columns[26:]

    X_train = df[df.columns[:26]]

    inputs = keras.Input(shape=(X_train.shape[1],), name='digits')
    x = Dense(100, activation='relu', name='dense_1')(inputs)
    x = Dense(250, activation='relu', name='dense_2')(x)
    outputs = Dense(categories.size, name='predictions')(x)
    model = keras.Model(inputs=inputs, outputs=outputs)

    model.compile(optimizer='adam', loss=tf.nn.softmax_cross_entropy_with_logits, metrics=['accuracy'])

    model.fit(X_train, y_train, epochs=15, batch_size=64, verbose=0)

    model_json = model.to_json()

    with open(FILENAME_MODEL, "w") as json_file:
        json_file.write(model_json)

    model.save_weights(FILENAME_WEIGHTS)

# Загрузка модели
# from keras.models import load_model
# from keras.models import model_from_json
# from keras.models import load_model

# json_file = open(FILENAME_MODEL, 'r')

# loaded_model_json = json_file.read()
# json_file.close()
# loaded_model = model_from_json(loaded_model_json)

# loaded_model.load_weights(FILENAME_WEIGHTS)

# m = model2(loaded_model)
