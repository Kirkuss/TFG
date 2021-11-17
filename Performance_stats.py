import matplotlib.pyplot as plt

def isolation_performance_plot(list_x, list_y, x_axis, y_axis, title):
    plt.plot(list_x, list_y)
    plt.xlabel(x_axis)
    plt.ylabel(y_axis)
    plt.title(title)
    plt.show()

def showStats(iterations, lenght, postProcessing):
    if postProcessing:
        perc = (iterations/lenght) * 100
        print('\r', "| Preprocessing... " + str(int(perc)) + "%", end='')
    elif not postProcessing:
        perc = (iterations/lenght) * 100
        print('\r', "| Postprocessing... " + str(int(perc)) + "%", end='')