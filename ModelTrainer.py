"""
Model dataset -> https://www.kaggle.com/msambare/fer2013
"""
import gc
import math

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import  layers
import cv2
import os
import matplotlib.pyplot as plt
import numpy as np
import variables as config
import random

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

def generateModel():
    Classes = ["angry", "disgust", "fear", "happy", "neutral", "sad", "surprise"]
    trainData = []

    X = []
    y = []

    createTrainData(Classes, trainData)
    random.shuffle(trainData)

    itemNum = len(trainData)
    var = itemNum
    iterations = 0
    test = 0
    aux = 2000

    while test is not itemNum:
        var = var - aux
        if var < 0:
            aux = itemNum - test
            return var
        else:
            test += aux
        print("[VAR]: " + str(var))
        print("[TEST]: " + str(test))
        pass


    for features, label in trainData:
        X.append(features)
        y.append(label)

    print("X: " + str(len(X)))
    #print("Floor: " + str(int(itenNumPair)))
    exit(1)

    X = np.array(X).reshape(-1, config.IMG_SIZE_PROC, config.IMG_SIZE_PROC, 3) #la arquitectura MobileNet necesita 4 dimensiones
    X = X/255.0;
    #print(len(X))
    #X = X/255.0; #Normalizamos (el rango maximo RGB es 255)
    Y = np.array(y)

    model = tf.keras.applications.MobileNetV2()

    #Transfer learning

    baseInput = model.layers[0].input
    baseOutput = model.layers[-2].output

    finalOutput = layers.Dense(128)(baseOutput)
    finalOuput = layers.Activation('relu')(finalOutput)
    finalOutput = layers.Dense(64)(finalOuput)
    finalOuput = layers.Activation('relu')(finalOutput)
    finalOutput = layers.Dense(7,activation='softmax')(finalOuput) #7 clases (enfadado, contento, etc...)

    newModel = keras.Model(inputs = baseInput, outputs = finalOutput)
    newModel.compile(loss="sparse_categorical_crossentropy", optimizer="adam", metrics=["accuracy"])
    newModel.fit(X,Y, epochs=25)
    newModel.save(config.EMOTION_MODEL)

