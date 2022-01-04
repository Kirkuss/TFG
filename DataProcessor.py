import matplotlib.pyplot as plt
import numpy as np
import scipy as sp
from scipy import interpolate

from Utilities import jsonManager as js

data = {}

predResults_GLOBAL = {"angry": 0, "disgust": 0, "fear": 0, "happy": 0, "neutral": 0, "sad": 0, "surprise": 0}

def startProcessingData(frames):
    data = js.loadJson(js, path="Resources/jsonFiles/PostProcessResults.json").copy()
    print("Y: " + str(len(data)))
    for i in data:
        for j in data[i]:
            predResults_GLOBAL[data[i][j]["pred"]] += 1

    #BARPLOT

    """
    labels = []
    sizes = []

    for i in predResults_GLOBAL:
        labels.append(i)
        sizes.append(predResults_GLOBAL[i])

    fig1 = plt.figure()
    ax1 = fig1.add_axes([0,0,1,1])
    ax1.set_ylabel("Ocurrences")
    ax1.set_xlabel("Prediction")
    ax1.set_title("Global predictions")
    ax1.bar(labels, sizes)

    plt.show()
    """

    #LINE PLOT

    records = []

    x = list(range(1, frames + 1))
    x_new = np.linspace(1, frames, 1000)
    y = [0] * len(x)

    for k in predResults_GLOBAL:
        for i in data:
            for j in data[i]:
                var = data[i][j]["pred"]
                if var == k:
                    y[int(j) - 1] += 1
        a_BSpline = sp.interpolate.make_interp_spline(x, y)
        y_new = a_BSpline(x_new)
        plt.plot(x_new, y_new, label=k)
        y.clear()
        y = [0] * len(x)

    plt.legend()
    plt.xlabel("Frames")
    plt.ylabel("Occurrences")
    plt.title("Predictions per frame")
    plt.show()

    print(predResults_GLOBAL)