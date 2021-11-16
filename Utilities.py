import json

def serializeFace(face, id):
    serialized = {}
    serialized[str(id)] = face.getSerialized()
    for k in face.list:
        serialized[str(face.list[k].frame)] = (face.list[k].getSerialized())
    return serialized

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
        pass

    def saveJson(self, path):
        with open(path, 'w') as outfile:
            json.dump(self.data,outfile, indent=4, sort_keys=True)
