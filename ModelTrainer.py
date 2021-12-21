"""
Model dataset -> https://www.kaggle.com/msambare/fer2013
"""
import gc
import itertools
import math

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
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

def createValidationData(Classes, validationData):
    for c in Classes:
        path = os.path.join("Resources/datasets/test", c)
        classNum = Classes.index(c)
        for img in os.listdir(path):
            try:
                frame = cv2.imread(os.path.join(path, img))
                resizedFrame = cv2.resize(frame, (config.IMG_SIZE_PROC, config.IMG_SIZE_PROC))
                validationData.append([resizedFrame, classNum])
            except Exception as e:
                pass

def chunkClasses(lst):
    X = []
    Y = []
    for features, label in lst:
        X.append(features)
        Y.append(label)
    X = np.array(X).reshape(-1, config.IMG_SIZE_PROC, config.IMG_SIZE_PROC, 3)
    X = X / 255.0;
    Y = np.array(Y)
    return X, Y

def chunk(lst, n):
    for i in range(0, len(lst), n):
        yield chunkClasses(lst[i:i + n])

def progress(n, s):
    pro = (n/s)*100
    pro = round(pro, 2)
    print(f"[PROGRESS]: {pro}%")

def repeatProcess(n):
    i = 0
    while i<n:
        Classes = ["angry", "disgust", "fear", "happy", "neutral", "sad", "surprise"]
        trainData = []
        validationData = []

        createTrainData(Classes, trainData)
        createValidationData(Classes, validationData)
        random.shuffle(trainData)
        random.shuffle(validationData)

        gpus = tf.config.list_physical_devices('GPU')
        if gpus:
            try:
                for gpu in gpus:
                    tf.config.experimental.set_memory_growth(gpu, True)
                    # tf.config.set_logical_device_configuration(
                    #   gpus[0],
                    #   [tf.config.LogicalDeviceConfiguration(memory_limit=4096)])
                logical_gpus = tf.config.list_logical_devices('GPU')
                print(len(gpus), "Physical GPUs, ", len(logical_gpus), "Logical GPUs")
            except RuntimeError as e:
                print(e)

        model = tf.keras.applications.MobileNetV2()

        baseInput = model.layers[0].input
        baseOutput = model.layers[-2].output

        finalOutput = layers.Dense(128)(baseOutput)
        finalOuput = layers.Activation('relu')(finalOutput)
        finalOutput = layers.Dense(64)(finalOuput)
        finalOuput = layers.Activation('relu')(finalOutput)
        finalOutput = layers.Dense(7, activation='softmax')(finalOuput)  # 7 clases (enfadado, contento, etc...)

        newModel = keras.Model(inputs=baseInput, outputs=finalOutput)
        newModel.compile(loss="sparse_categorical_crossentropy", optimizer="adam", metrics=["accuracy"])

        # iterations = 0
        batch_size = 10
        epochs = 10

        print(len(trainData))
        print(len(validationData))

        epoch_steps = int(len(trainData) / batch_size) / 10
        validation_steps = int(len(validationData) / batch_size) / 10

        print(epoch_steps)
        print(validation_steps)

        newModel.load_weights(config.EMOTION_MODEL)

        newModel.fit(chunk(trainData, batch_size), epochs=epochs, steps_per_epoch=epoch_steps)
        # validation_data=validation, validation_steps=validation_steps)
        newModel.save_weights(config.EMOTION_MODEL)
        i += 1
        gc.collect()

    print("finished proc")
    return 0

def generateModel():
    hola = False
    if hola:

        Classes = ["angry", "disgust", "fear", "happy", "neutral", "sad", "surprise"]
        trainData = []
        validationData = []

        createTrainData(Classes, trainData)
        createValidationData(Classes, validationData)
        random.shuffle(trainData)
        random.shuffle(validationData)


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

        gpus = tf.config.list_physical_devices('GPU')
        if gpus:
            try:
                for gpu in gpus:
                    tf.config.experimental.set_memory_growth(gpu, True)
                    #tf.config.set_logical_device_configuration(
                    #   gpus[0],
                    #   [tf.config.LogicalDeviceConfiguration(memory_limit=4096)])
                logical_gpus = tf.config.list_logical_devices('GPU')
                print(len(gpus), "Physical GPUs, ", len(logical_gpus), "Logical GPUs")
            except RuntimeError as e:
                print(e)

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

        #iterations = 0
        batch_size = 10
        epochs = 10

        print(len(trainData))
        print(len(validationData))

        epoch_steps = int(len(trainData)/batch_size)/10
        validation_steps = int(len(validationData)/batch_size)/10

        print(epoch_steps)
        print(validation_steps)

        #train = chunk(trainData, batch_size)
        #validation = chunk(validationData, batch_size)

        newModel.fit(chunk(trainData, batch_size), epochs=epochs, steps_per_epoch=epoch_steps)
                               #validation_data=validation, validation_steps=validation_steps)
        newModel.save_weights(config.EMOTION_MODEL)

        gc.collect()

    repeatProcess(10)

    #EL YIELD SIGUE DEVOLVIENDO DATOS DESPUES DEL PRIMER EPOCH SIN QUE EMPIECE EL SEGUNDO, LO QUE HACE QUE AL LLEGAR
    #A 7170 (NUMERO DE DATOS EN LA LISTA DE TEST) SE QUEDE SIN DATOS CON LOS QUE TRABAJAR Y PETE

    """
    for i in list(chunk(trainData, batch_size)):
        #if iterations == 2:
        #   break
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
 
        if iterations == 0:
           pass
        else:
           newModel.load_weights(config.EMOTION_MODEL)
        print ("[YIELD]: " + str(len(i)))
        for features, label in i:
                X.append(features)
                Y.append(label)
        X = np.array(X).reshape(-1, config.IMG_SIZE_PROC, config.IMG_SIZE_PROC, 3)
        X = X / 255.0;
        Y = np.array(Y)
        newModel.fit(X, Y, epochs=epochs)
        newModel.save_weights(config.EMOTION_MODEL)
        X = []
        Y = []
        n += len(i)
        progress(n, sizeOf)
        #del X
        #del Y
        #del newModel
        gc.collect()
        #break
        iterations += 1

    #newModel.save("Resources/datasets/Models/prueba.h5")
    while(1):
        pass
    """

