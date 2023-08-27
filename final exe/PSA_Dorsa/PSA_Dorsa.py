import sys
from PyQt5.QtWidgets import QDialog , QApplication,QSplashScreen,QMainWindow
from PyQt5.uic import loadUi
from PyQt5.QtCore import Qt , QTimer
from PyQt5.QtGui import QPixmap
import time
from main import Ui

class splashscreen (QDialog):
    def __init__(self):
        self.counter = 0
        self.n = 200 # total instance


        self.timer = QTimer()
        self.timer.timeout.connect(self.progress)
        self.timer.start(30)



        super(QDialog,self).__init__()
        loadUi("splash.ui",self)
        self.setWindowFlag(Qt.FramelessWindowHint)
        # pixmap = QPixmap("Icons/pellet.jpg")
        # self.setPixmap(pixmap)

    # def progress (self) :
    #     for i in range(101):
    #         time.sleep(0.01)
    #         # print(i)
    #         self.progressBar.setValue(i)

    def progress(self):
        self.progressBar.setValue(self.counter)

        if self.counter == int(self.n * 0.3):
            pass
            # self.labelDescription.setText('<strong>Working on Task #2</strong>')
        elif self.counter == int(self.n * 0.6):
            pass
            # self.labelDescription.setText('<strong>Working on Task #3</strong>')
        elif self.counter >= self.n:
            self.timer.stop()
            self.close()

            time.sleep(1)

            # MyApp = loadUi("main_UI.ui",self)
            # self.setWindowFlag(Qt.FramelessWindowHint)
            self.myApp = Ui()
            self.myApp.show()

        self.counter += 1


if __name__ == '__main__':
    app = QApplication(sys.argv)
    splash_screen = splashscreen()
    splash_screen.show()
    splash_screen.progress()

    app.exec_()


# self.show_message(label_name=None, text=texts.MESSEGES['reset_data'][self.language], level=1, clearable=True)
