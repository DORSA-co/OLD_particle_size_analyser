from PyQt5 import QtWidgets, QtCore, QtGui
import numpy as np



class PhotoViewer(QtWidgets.QGraphicsView):
    def __init__(self):
        super(PhotoViewer, self).__init__()

        self.first_fit = False
        self.zoom = 0
        self.empty = True
        self.scene = QtWidgets.QGraphicsScene(self)
        self.photo = QtWidgets.QGraphicsPixmapItem()
        self.scene.addItem(self.photo)
        self.setScene(self.scene)
        self.setTransformationAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        #self.setBackgroundBrush(sQtGui.QBrush(sQtGui.QColor(30, 30, 30)))
        self.setFrameShape(QtWidgets.QFrame.NoFrame)
        #
        self.base_image = None
        self.pen = QtGui.QPen(QtCore.Qt.white, 1)
        self.grid_shape = [15, 24]
        self.crosshair_shape = [2 ,2]
        self.grid = 0 # 0, 1 (crosshair), or 2 (grid)
    

    def hasPhoto(self):
        return not self.empty


    def fitInView(self, scale=True):
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
                self.scale(factor, factor)

            self.zoom = 0
    

    def add_grid_to_image(self, grid_type=0):
        pixmap = self.base_image.copy()
        row = pixmap.height()
        col = pixmap.width()
        rows, cols = self.crosshair_shape if grid_type==0 else self.grid_shape
        dy, dx = row / rows, col / cols

        painter = QtGui.QPainter(pixmap)
        painter.setPen(self.pen)

        # draw vertical lines
        for x in np.linspace(start=dx, stop=col-dx, num=cols-1):
            x = int(round(x))
            painter.drawLine(x, 0, x, row)
        # draw horizontal lines
        for y in np.linspace(start=dy, stop=row-dy, num=rows-1):
            y = int(round(y))
            painter.drawLine(0, y, col, y)

        return pixmap
    
    
    def enable_grid(self, grid_type=1):
        if grid_type == self.grid:
            self.grid = 0
        else:
            self.grid = grid_type
        #
        self.setPhoto(add_grid_event=True)


    def setPhoto(self, pixmap=None, raw=False, add_grid_event=False):
        # keep basse image
        if not add_grid_event:
            self.base_image = pixmap

        # add grid if needed
        if self.base_image is not None:
            pixmap = self.add_grid_to_image(grid_type=self.grid-1) if self.grid>0 else self.base_image
    
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
            if event.angleDelta().y() > 0:
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
    

    def strech(self):
        if self.hasPhoto():
            self.zoom = 0
            self.fitInView()