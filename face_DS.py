import cv2

class face:
    def __init__(self, x, y, w, h, id):
        self.id = id
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        # self.visited = False ?

    #Metodo equal:
    # comprueba que un punto dado esta en un area si coincide
    # con el area del punto de la cara anterior
    # la cara es la misma y actualiza el estado

    def equal(self, conf, x, y, frame):
        x1, y1 = int(self.x + (self.w * conf)),int(self.y + (self.h * conf))
        x2, y2 = int(self.x - (self.w * conf)),int(self.y - (self.h * conf))

        if x2 < 0: x2 = 0
        elif y2 < 0: y2 = 0

        rx = range(x2, x1 + 1)
        ry = range(y2, y1 + 1)

        #print(str(x2) + " " + str(y2) + " " + str(x1) + " " + str(y1))

        cv2.rectangle(frame, (x2, y2), (x1, y1), (0, 255, 0), 1)

        if x in rx and y in ry:
            return True
        else:
            return False

    def toString(self):
        return ("face: (" + str(self.x) + ", " + str(self.y) + ") w: " + str(self.w) + " h: " + str(self.h))


class dataList:
    def __init__(self, item, next = None):
        self.item = item
        self.next = next

    def getNext(self): return self.next

    def getItemById(self, id):
        while self.next is not None:
            if self.item.id == id: return self.item
            else: return self.next.getItemById(id)
        return None

    def updateItem(self, item):
        self.item.x = item.x
        self.item.y = item.y
        self.item.w = item.w
        self.item.h = item.h

    def countItems(self):
        if self.item is None: count = 0
        else: count = 1
        while self.next is not None:
            count += self.next.countItems()
            pass

        return count







