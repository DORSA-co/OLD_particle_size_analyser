# import pickle
# import numpy as np
# import os

# REPORTS_MAIN_PATH = 'reports'
# CONTOURS_JSON_NAME = 'contours.pickle'
# #
# GRADING_PARAMS_JSON_NAME = 'grading_params.pickle'
# CALIBRATION_COEFS_KEY = 'calib_coefs'
# CIRCLE_ACC_THRS_KEY = 'circ_acc_thrs'
# GRADING_RANGES_KEY = 'grading_ranges'


# grading_params = {CALIBRATION_COEFS_KEY: np.array([0, 0, 0.018]),
#                         CIRCLE_ACC_THRS_KEY: 0.8,
#                         GRADING_RANGES_KEY: {0:[1,2], 1:[2,3]}}

# with open(GRADING_PARAMS_JSON_NAME, 'wb') as handle:
#     pickle.dump(grading_params, handle, protocol=pickle.HIGHEST_PROTOCOL)

import sys
import matplotlib
matplotlib.use('Qt5Agg')

from PyQt5 import QtCore, QtWidgets

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure


class MplCanvas(FigureCanvasQTAgg):

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super(MplCanvas, self).__init__(fig)


class MainWindow(QtWidgets.QMainWindow):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        # Create the maptlotlib FigureCanvas object,
        # which defines a single set of axes as self.axes.
        sc = MplCanvas(self, width=5, height=4, dpi=100)
        sc.axes.plot([0,1,2,3,4], [10,1,20,3,40])
        self.setCentralWidget(sc)

        self.show()


app = QtWidgets.QApplication(sys.argv)
w = MainWindow()
app.exec_()