#!/usr/bin/env python
# coding: utf-8

# In[2]:


import keras
import tensorflow as tf
from keras.layers import Dense
from sklearn.preprocessing import OneHotEncoder
from sklearn.metrics import roc_auc_score
import pandas as pd
import numpy as np
from scipy.special import softmax
from models.metrics import hitrate
from sklearn.model_selection import train_test_split
from models.product import getTopInCategory
import pickle

FILENAME = 'data/finalized_model_2.sav'

def learn_model2:
    df = pd.read_csv('training_sample.csv').fillna(0)

    df = df.sample(frac=1)

    y_train = df.BU_Level4
    self.categories = y_train.unique()
    y_train = pd.get_dummies(y_train)

    X_train = df.drop(['BU_Level4', 'ItemEAN'], axis = 1)
        
    inputs = keras.Input(shape=(X_train.shape[1],), name='digits')
    x = Dense(100, activation='relu', name='dense_1')(inputs)
    x = Dense(250, activation='relu', name='dense_2')(x)
    outputs = Dense(self.categories.size, name='predictions')(x)
    self.model = keras.Model(inputs=inputs, outputs=outputs)
        
    self.model.compile(optimizer='adam', loss=tf.nn.softmax_cross_entropy_with_logits, metrics=['accuracy'])
        
    self.model.fit(X_train, y_train, epochs=25, batch_size=32, verbose=0)
    
    pickle.dump(model, open(FILENAME, 'wb'))

class model2():
    def __init__(self, load_model, k = 5, n = 1):
        self.model = load_model
        self.categories_ya = []
        self.categories = []
        self.criterion = {}
        self.k = k
        self.n = n
        
        self.categories_ya = pd.read_csv('data/categories_with_yandex.csv')

        df = pd.read_csv('data/training_sample.csv').fillna(0)
        
        self.categories = df.BU_Level4.unique()

    def predict(self, X_test):
        return softmax(self.model.predict(X_test), axis = 1)
    
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
        
    def get_gifts_(self, X_test, hobby=[], max_cost = 10000, min_cost = 0):
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
        
        


def get_gifts(X_test, hobby=[], max_cost = 10000, min_cost = 0):
    loaded_model = pickle.load(open(FILENAME, 'rb'))
    model = model2(loaded_model)
    return model.get_gifts_(X_test, hobby, max_cost, min_cost)

