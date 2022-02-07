import json
import datetime
import time

from PyQt5.QtCore import pyqtSignal, QThread

def serializeFace(face, id):
    serialized = {}
    serialized[str(id)] = face.getSerialized()
    for k in face.list:
        serialized[str(face.list[k].frame)] = (face.list[k].getSerialized())
    return serialized

class timeStamp():
    def getTime(self):
        now = datetime.datetime.now()
        return "[" + '{:02d}'.format(now.hour) + ":" + '{:02d}'.format(now.minute) + ":" + '{:02d}'.format(now.second) + "]"

class ModelInterpreter():
    Classes = ["angry", "disgust", "fear", "happy", "neutral", "sad", "surprise"]

    def getClass(n):
        return ModelInterpreter.Classes[n]

class jsonManager(object):

    __instance = None
    data = {}

    def __new__(cls):
        if jsonManager.__instance is None:
            jsonManager.__instance = object.__new__(cls)
        return jsonManager.__instance

    def setData(self, data, type):
        aux = {}
        if type == "face":
            for k in data:
                aux[str(k)] = serializeFace(data[k], k) #ordenara segun la id de la cara (valida, pues la lista viene limpia)

        self.data = aux.copy()

    def loadJson(self, path):
        """
        Aqui se leeran los archivos que se vayan guardando y se devolvera un diccionario para procesarlos, la idea
        es ocupar el minimo espacio en la memoria mientras se procesa de manera que una vez preprocesados los datos
        de video, un archivo json contenga los resultados de dicho preprocesamieto, de esta manera se pueden guardar
        dichos datos para analizar despues, el programa es mas rapido y ademas, podremos ver los datos producidos por
        el preprocesamiento en un fichero json fuera de la ejecucion del programa.

        Ademas, algo bastante importante es que se van a diferenciar mas aun las etapas de la ejecucion, es decir,
        postprocesado no va a necesitar que se haga el preprocesado si ya existe el archivo json, pudiendo asi modificar
        la etapa del preprocesado sin necesidad de que dichos cambios afecten a la siguiente etapa.
        """
        with open (path) as f:
            data = json.load(f)
        return data
        #print(data) , sort_keys=True



    def saveJson(self, path):
        with open(path, 'w') as outfile:
            json.dump(self.data,outfile, indent=4)
        self.data.clear()

class threadManager(QThread):

    unlock = pyqtSignal(int)
    pool = {}
    iteration = 1
    result = 0
    poolSize = 0
    
    def __init__(self, parent=None):
        super(threadManager, self).__init__(parent)
        self.running = True
        self.parent = parent
        self.pool = {}

    def addToPool(self, worker, i):
        self.pool[i] = worker
        self.pool[i].start()


    """
    def checkStatus(self, id, status, iteration):
        
        print("Mensaje recibido de: " + str(id) + " Status: " + str(status) + " en la iteracion: " + str(iteration) + "\n")
        if status == 1 and iteration == self.iteration:
            self.result += 1

        if self.result == self.poolSize:
            self.unlock.emit(1)
            self.iteration += 1
    """




"""
                            if int(j) == iterations:

                                cropped = frame[int(self.faces[i][j]["y"]):int(self.faces[i][j]["y"]) + int(self.faces[i][j]["h"]),
                                          int(self.faces[i][j]["x"]):int(self.faces[i][j]["x"])+int(self.faces[i][j]["w"])]
                                #cropped = cv2.cvtColor(cropped, cv2.COLOR_BGR2GRAY)
                                resized = cv2.resize(cropped, (224,224))
                                resized = np.expand_dims(resized, axis=0)
                                resized = resized/255.0
                                predictions = self.model.predict(resized, verbose=0)
                                pred = mi.getClass(n = np.argmax(predictions))
                                self.faces[i][j]["pred"] = pred
                                #print(predictions[0])
                                cv2.rectangle(frame, (int(self.faces[i][j]["x"]),int(self.faces[i][j]["y"])),
                                              (int(self.faces[i][j]["x"]) + int(self.faces[i][j]["w"]),
                                               int(self.faces[i][j]["y"]) + int(self.faces[i][j]["h"])),
                                              (255, 255, 255), 1)
                                cv2.putText(frame, "ID " + i + pred,
                                            (int(int(self.faces[i][j]["x"])) + 5, int(self.faces[i][j]["y"]) - 7),
                                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)

                                break #occurrence found, break first j for loop.
                                """
