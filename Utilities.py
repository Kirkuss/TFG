import json

class jsonManager(object):

    __instance = None
    data = {}

    def __new__(cls):
        if jsonManager.__instance is None:
            jsonManager.__instance = object.__new__(cls)
        return jsonManager.__instance

    def setData(self, data):
        self.data = data

    def loadJson(self, path):
        """
        Aqui se leeran los archivos que se vayan guardando y se devolvera un diccionario para procesarlos, la idea
        es ocupar el minimo espacio en la memoria mientras se procesa de manera que una vez preprocesados los datos
        de video, un archivo json contenga los resultados de dicho preprocesamieto, de esta manera se pueden guardar
        dichos datos para analizar despues, el programa es mas rapido y ademas, podremos ver los datos producidos por
        el preprocesamiento en un fichero json fuera de la ejecucion del programa.
        """
        pass

    def saveJson(self, path):
        with open(path, 'w') as outfile:
            json.dump(self.data, outfile)
