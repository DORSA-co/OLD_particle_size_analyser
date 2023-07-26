import sys
import cv2
from functools import partial
from PyQt5 import QtWidgets, uic, QtCore, QtGui


class about_Ui(QtWidgets.QMainWindow):
    """this class is used to build class for about UI

    :about QtWidgets: _description_
    """

    def __init__(self, ui_obj):
        """this function is used to laod ui file and build GUI
        """

        super(about_Ui, self).__init__()

        # load ui file
        uic.loadUi('about_ui.ui', self)
        self.setWindowFlags(QtCore.Qt.WindowFlags(QtCore.Qt.FramelessWindowHint))

        # language
        self.ui_obj = ui_obj
        try:
            self.language = ui_obj.language
        except:
            self.language = 'en'
        
        self.win_open = False
        self._old_pos = None

        #
        self.button_connector()
    

    def button_connector(self):
        """this function is used to connect ui buttons to their functions
        """

        # top window buttons
        self.close_btn.clicked.connect(partial(self.close_win))


    def mousePressEvent(self, event):
        """mouse press event for moving window

        :param event: _description_
        """

        # accept event only on top and side bars and on top bar
        if event.button() == QtCore.Qt.LeftButton and not self.isMaximized() and event.pos().y()<=self.header.height():
            self._old_pos = event.globalPos()


    def mouseReleaseEvent(self, event):
        """mouse release event for stop moving window

        :param event: _description_
        """

        if event.button() == QtCore.Qt.LeftButton:
            self._old_pos = None


    def mouseMoveEvent(self, event):
        """mouse move event for moving window

        :param event: _description_
        """

        if self._old_pos is None:
            return

        delta = QtCore.QPoint(event.globalPos() - self._old_pos)
        self.move(self.x() + delta.x(), self.y() + delta.y())
        self._old_pos = event.globalPos()
    

    def close_win(self):
        """
        this function closes the window
        Inputs: None
        Returns: None
        """

        # close app window and exit the program
        self.win_open = False
        self.close()
    



if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = about_Ui(ui_obj=None)
    window.show()
    app.exec_()