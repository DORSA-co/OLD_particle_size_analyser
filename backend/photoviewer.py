from PyQt5 import QtWidgets, QtCore, QtGui



class PhotoViewer(QtWidgets.QGraphicsView):
    def __init__(self):
        super(PhotoViewer, self).__init__()

        self.first_fit = True
        self.zoom = 0
        self.empty = True
        self.scene = QtWidgets.QGraphicsScene(self)
        self.photo = QtWidgets.QGraphicsPixmapItem()
        self.scene.addItem(self.photo)
        self.setScene(self.scene)
        self.setTransformationAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
        # self.setResizeAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
        # self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        # self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        #self.setBackgroundBrush(sQtGui.QBrush(sQtGui.QColor(30, 30, 30)))
        self.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.fitInView()
        

    def hasPhoto(self):
        return not self.empty


    def fitInView(self, scale=True,ui=False):
        rect = QtCore.QRectF(self.photo.pixmap().rect())
        if not rect.isNull():
            self.setSceneRect(rect)
            if self.hasPhoto():
                unity = self.transform().mapRect(QtCore.QRectF(0, 0, 1, 1))
                self.scale(1 / unity.width(), 1 / unity.height())
                viewrect = self.viewport().rect()
                scenerect = self.transform().mapRect(rect)
                factor = min(viewrect.width() / scenerect.width(),
                             viewrect.height() / scenerect.height())
                if ui:
                    h= ui.image_frame.height()
                    w= ui.image_frame.width()

                    factor = min(w / scenerect.width(),
                            h / scenerect.height())               

                self.showFullScreen()
                
                self.scale(factor, factor)

            self.zoom = 0


    def setPhoto(self, pixmap=None):
        if not self.first_fit:
            self.zoom = 0

        if pixmap and not pixmap.isNull():
            self.empty = False
            self.setDragMode(QtWidgets.QGraphicsView.ScrollHandDrag)
            self.photo.setPixmap(pixmap)

        else:
            self.empty = True
            self.setDragMode(QtWidgets.QGraphicsView.NoDrag)
            self.photo.setPixmap(QtGui.QPixmap())

        if not self.first_fit:
            self.fitInView()
            self.first_fit = True


    def wheelEvent(self, event):
        if self.hasPhoto():
            self.fitInView()
            if event.angleDelta().y() > 0:
                factor = 0.8
                self.zoom += 1
            else:
                factor = 0.8
                self.zoom -= 1

            if self.zoom > 0:
                self.scale(factor, factor)
            elif self.zoom == 0:
                self.fitInView()
            else:
                self.zoom = 0
        
        else:
            pass


    def zoomin(self, reverse=False):
        if self.hasPhoto():
            if not reverse:
                factor = 1.25
                self.zoom += 1
            else:
                factor = 0.8
                self.zoom -= 1

            if self.zoom > 0:
                self.scale(factor, factor)
            elif self.zoom == 0:
                self.fitInView()
            else:
                self.zoom = 0
        
        else:
            pass

    