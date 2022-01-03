import matplotlib.pyplot as plt

from Utilities import jsonManager as js

data = {}

predResults_GLOBAL = {"angry": 0, "disgust": 0, "fear": 0, "happy": 0, "neutral": 0, "sad": 0, "surprise": 0}

def startProcessingData():
    data = js.loadJson(js, path="Resources/jsonFiles/PostProcessResults.json").copy()
    print("Y: " + str(len(data)))
    for i in data:
        for j in data[i]:
            predResults_GLOBAL[data[i][j]["pred"]] += 1

    #PIE

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

    print(predResults_GLOBAL)