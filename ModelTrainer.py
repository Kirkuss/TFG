"""
Model dataset -> https://www.kaggle.com/msambare/fer2013
"""
import gc
import math

import tensorflow as tf
import keras
from keras import layers
import cv2
import os
import matplotlib.pyplot as plt
import numpy as np
import variables as config
import random
#from tensorflow.python.client import device_lib

def createTrainData(Classes, trainData):
    for c in Classes:
        path = os.path.join(config.DATA_DIRECTORY, c)
        classNum = Classes.index(c)
        for img in os.listdir(path):
            try:
                frame = cv2.imread(os.path.join(path, img))
                resizedFrame = cv2.resize(frame, (config.IMG_SIZE_PROC, config.IMG_SIZE_PROC))
                trainData.append([resizedFrame, classNum])
            except Exception as e:
                pass

def chunk(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

def generateModel():
    Classes = ["angry", "disgust", "fear", "happy", "neutral", "sad", "surprise"]
    trainData = []

    X = []
    Y = []

    createTrainData(Classes, trainData)
    random.shuffle(trainData)

    aux = 1000

    #for features, label in trainData:
    #   X.append(features)
    #   y.append(label)

    """
        Bucle for para controlar el uso de la memoria al entrenar el modelo para las caras, funciona de la siguiente 
        manera:
        Keras permite entrenar sobre un modelo ya creado, es decir, los primeros 2000 elementos del DataSet formaran
        el modelo inicial y los siguientes 2000 lo seguiran entrenando, de esta forma no saturamos la memoria del equipo.
        yield (usado en la funcion chunk) devuelve una lista parcial de elementos que hace posible esto.
        Como el modelo es sobre emociones no hay riesgo de que "olvide" iteraciones anteriores (no varia de una iteracion
        a otra)
    """

    iteration = 0;

    for i in list(chunk(trainData, aux)):
        if iteration == 0:

            #print(device_lib.list_local_devices())
            #Kconf = tf.ConfigProto(device_count={'GPU': 1, 'CPU': 4})
            #sess = tf.Session(config=Kconf)
            #keras.backend.set_session(sess)

            model = tf.keras.applications.MobileNetV2()

            # Transfer learning

            baseInput = model.layers[0].input
            baseOutput = model.layers[-2].output

            finalOutput = layers.Dense(128)(baseOutput)
            finalOuput = layers.Activation('relu')(finalOutput)
            finalOutput = layers.Dense(64)(finalOuput)
            finalOuput = layers.Activation('relu')(finalOutput)
            finalOutput = layers.Dense(7, activation='softmax')(finalOuput)  # 7 clases (enfadado, contento, etc...)

            newModel = keras.Model(inputs=baseInput, outputs=finalOutput)
            newModel.compile(loss="sparse_categorical_crossentropy", optimizer="adam", metrics=["accuracy"])
        else:

            #Kconf = tf.ConfigProto(device_count={'GPU': 1, 'CPU': 4})
            #sess = tf.Session(config=Kconf)
            #keras.backend.set_session(sess)

            model = tf.keras.applications.MobileNetV2()

            # Transfer learning

            baseInput = model.layers[0].input
            baseOutput = model.layers[-2].output

            finalOutput = layers.Dense(128)(baseOutput)
            finalOuput = layers.Activation('relu')(finalOutput)
            finalOutput = layers.Dense(64)(finalOuput)
            finalOuput = layers.Activation('relu')(finalOutput)
            finalOutput = layers.Dense(7, activation='softmax')(finalOuput)  # 7 clases (enfadado, contento, etc...)

            newModel = keras.Model(inputs=baseInput, outputs=finalOutput)
            newModel.compile(loss="sparse_categorical_crossentropy", optimizer="adam", metrics=["accuracy"])
            model = tf.keras.models.load_weights(config.EMOTION_MODEL)
        print ("[YIELD]: " + str(len(i)))
        for features, label in i:
                X.append(features)
                Y.append(label)
        X = np.array(X).reshape(-1, config.IMG_SIZE_PROC, config.IMG_SIZE_PROC, 3)
        X = X / 255.0;
        Y = np.array(Y)
        newModel.fit(X, Y, epochs=25)
        newModel.save_weights(config.EMOTION_MODEL)
        X = []
        Y = []

    exit(1)

