# import numpy as np
# import cv2
# import datetime
# from mycolorpy import colorlist as mcp
# from PIL import ImageColor

# from backend import date, texts



# def draw_contours_on_image(image, cnts):
#     """this function is used to draw contours of the founded edges

#     :param image: _description_
#     :param cnts: _description_
#     :return: _description_
#     """
#     if len(image.shape)<3:
#         image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
#     image = cv2.drawContours(image, cnts , -1, (0,255,0), thickness=1)
#     return image



# class Algo_Params():
#     """this class is used to get/manage grading algorithm params from ui

#     :return: _description_
#     """

#     def __init__(self, ui_obj, params_ui_obj):
#         self.ui_obj = ui_obj
#         self.params_ui_obj = params_ui_obj
#         self.ranges_dict = {}
#         self.ranges_colors = []
#         self.blur_ksize = None
#         self.gray_thrs = None
#         self.circ_acc = None
    

#     def update_params(self):
#         self.ranges_dict.clear()

#         # get ranges text from ui
#         ranges_text = self.params_ui_obj.ranges_textedit.toPlainText()
#         ranges = [item for item in ranges_text.splitlines() if item!='']

#         # validate ranges and add to ranges dict
#         for itr, range_ in enumerate(ranges):
#             try:
#                 self.ranges_dict[itr] = [float(range_.split('-')[0]), float(range_.split('-')[1])]
#             except:
#                 _ = self.ui_obj.show_alert_window(title=texts.TITLES['error'][self.ui_obj.language], message=texts.WARNINGS['algo_params_incorrect'][self.ui_obj.language], need_confirm=False)
#                 return
#         self.ranges_colors = mcp.gen_color(cmap='jet', n=len(self.ranges_dict.keys()))
        
#         # other parameters
#         self.blur_ksize = self.params_ui_obj.blur_ksize_spin.value()
#         self.blur_ksize = self.blur_ksize if self.blur_ksize%2==1 else self.blur_ksize+1
#         self.gray_thrs = self.params_ui_obj.gray_spin.value()
#         self.circ_acc = self.params_ui_obj.circ_acc_spin.value()
#         self.circ_acc = self.circ_acc if self.circ_acc<=1 else self.circ_acc/100
#         self.px_value = self.params_ui_obj.pxvalue_spin.value()



# class Grading():
#     """this class is used to grading
#     """

#     def __init__(self, algo_parasm_obj, debug=True, debug_scale=0.5):
#         # hyper params
#         self.debug = debug
#         self.debug_scale = debug_scale
#         self.algo_parasm_obj = algo_parasm_obj
#         #
#         self.grading_ranges_arr = None
#         self.n_objects = 0
#         self.circle_acc = []

    

#     def start_new_detection(self):
#         """this function is used to start new detection session
#         """

#         self.start_time = date.get_time()
#         self.start_date = date.get_date()
#         self.grading_ranges_arr = np.zeros((len(self.algo_parasm_obj.ranges_dict.keys())))
#         self.n_objects = 0
#         self.circle_acc = []
    

#     def end_detection(self):
#         """this function is used to end a detection session and return results
#         """

#         self.end_time = date.get_time()
#         #


    
#     def detect(self, image):  
#         # rgb to gray
#         gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape)>2 else image
#         if self.debug:
#             cv2.imshow('Gray Image', cv2.resize(gray, None, fx=self.debug_scale, fy=self.debug_scale))
#             cv2.waitKey(0)

#         # histogram equalization
#         clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(3, 3))
#         gray = clahe.apply(gray)
#         if self.debug:
#             cv2.imshow('Histogram Equalization', cv2.resize(gray, None, fx=self.debug_scale, fy=self.debug_scale))
#             cv2.waitKey(0)

#         # bulr image
#         gray = cv2.blur(gray, (self.algo_parasm_obj.blur_ksize, self.algo_parasm_obj.blur_ksize))
#         if self.debug:
#             cv2.imshow('Image Bluring', cv2.resize(gray, None, fx=self.debug_scale, fy=self.debug_scale))
#             cv2.waitKey(0)

#         # gray threshold
#         _, objects_mask = cv2.threshold(gray, self.algo_parasm_obj.gray_thrs, 255, cv2.THRESH_BINARY)
#         if self.debug:
#             cv2.imshow('Objects Mask', cv2.resize(objects_mask, None, fx=self.debug_scale, fy=self.debug_scale))
#             cv2.waitKey(0)

#         # find contours
#         contours, _ = cv2.findContours(objects_mask, cv2.RETR_LIST, cv2.CHAIN_APPROX_TC89_L1)
#         if self.debug:
#             cv2.imshow('Object Contours', cv2.resize(draw_contours_on_image(image=gray, cnts=contours), None, fx=self.debug_scale, fy=self.debug_scale))
#             cv2.waitKey(0)

#         # grading
#         for cnt in contours:
#             # get contour cordinates
#             (x,y), r = cv2.minEnclosingCircle(cnt)
#             x, y, w, h = cv2.boundingRect(cnt)
#             area = cv2.contourArea(cnt)

#             # get r
#             radius = min(w, h, r)
#             radius_mm = radius * self.algo_parasm_obj.px_value

#             # reject those object that arent circular enoug or have size not in desired range
#             if area / (np.pi * radius * radius) < self.algo_parasm_obj.circ_acc or not (self.algo_parasm_obj.ranges_dict[0][0]<=radius_mm<self.algo_parasm_obj.ranges_dict[len(self.algo_parasm_obj.ranges_dict.keys())-1][1]):
#                 continue

#             # update count
#             self.n_objects+=1

#             # circular acc
#             circ_acc = min(w, h) / max(w, h)
#             self.circle_acc.append(circ_acc)

#             # grading
#             for key in self.algo_parasm_obj.ranges_dict.keys():
#                 if self.algo_parasm_obj.ranges_dict[key][0] <= radius_mm < self.algo_parasm_obj.ranges_dict[key][1]:
#                     # draw contour on image
#                     cv2.drawContours(image, [cnt], -1, ImageColor.getcolor(self.algo_parasm_obj.ranges_colors[key], 'RGB'), 3)
                    
#                     # add tp grading arr
#                     self.grading_ranges_arr[key]+=1
        
#         # get ranges percentages
#         if  self.grading_ranges_arr.sum() != 0:
#             self.grading_ranges_arr = self.grading_ranges_arr / self.grading_ranges_arr.sum() * 100
        
#         if self.debug:
#             cv2.imshow('Grading Results', cv2.resize(image, None, fx=self.debug_scale, fy=self.debug_scale))
#             cv2.waitKey(0)

#         return image, self.grading_ranges_arr, np.array(self.circle_acc).mean()


# if __name__=='__main__':
#     path = 'C:/Users/Dorsa-PC/Desktop'
#     Grad_test = Grading()
#     import os
#     for fname in os.listdir(path):
#         image = cv2.imread(os.path.join( path, fname))  
#         image_res,range_grade,Mean_range = Grad_test.detect(image,0.25)
#         cv2.imshow('Smart Laboratory Grading System ',cv2.resize(image_res,None, fx=0.3,fy=0.3))
#         cv2.waitKey(50)

import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtChart import QChart, QBarSet, QBarSeries, QBarCategoryAxis, QValueAxis, QChartView, QCategoryAxis
from PyQt5.QtCore import QPoint
from PyQt5.Qt import QPen, QFont, Qt, QSize
from PyQt5.QtGui import QColor, QBrush, QLinearGradient, QGradient, QPainter
from PyQt5 import QtCore


class MyChart(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Chart Formatting Demo')
        self.resize(1200, 800)

        self.initChart()

        self.setCentralWidget(self.chartView)

    def initChart(self):
        series = QBarSeries()
        series.setLabelsVisible(True)
        # series.labelsPosition()
        circ_barset = QBarSet('test')
        data = [10, 20, 30, 40, 50]
        for i in range(len(data)):
            circ_barset.append(data[i])

        series.append(circ_barset)

        # creating chart object
        chart = QChart()
        chart.legend().hide()
        chart.addSeries(series)


        # pen = QPen(QColor(200, 200, 200))
        # pen.setWidth(5)
        # series.setPen(pen)


        font = QFont('Open Sans')
        font.setPixelSize(40)
        font.setBold(True)
        chart.setTitleFont(font)
        chart.setTitleBrush(QBrush(Qt.yellow))
        chart.setTitle('Custom Chart Demo')


        backgroundGradient = QLinearGradient()
        backgroundGradient.setStart(QPoint(0, 0))
        backgroundGradient.setFinalStop(QPoint(0, 1))
        backgroundGradient.setColorAt(0.0, QColor(175, 201, 182))
        backgroundGradient.setColorAt(1.0, QColor(51, 105, 66))
        backgroundGradient.setCoordinateMode(QGradient.ObjectBoundingMode)
        chart.setBackgroundBrush(backgroundGradient)


        plotAreaGraident = QLinearGradient()
        plotAreaGraident.setStart(QPoint(0, 1))
        plotAreaGraident.setFinalStop(QPoint(1, 0))
        plotAreaGraident.setColorAt(0.0, QColor(222, 222, 222))
        plotAreaGraident.setColorAt(1.0, QColor(51, 105, 66))
        plotAreaGraident.setCoordinateMode(QGradient.ObjectBoundingMode)
        chart.setPlotAreaBackgroundBrush(plotAreaGraident)
        chart.setPlotAreaBackgroundVisible(True)

        # customize axis
        axisX = QBarCategoryAxis()
        axisY = QBarCategoryAxis()

        labelFont = QFont('Open Sans')
        labelFont.setPixelSize(25)

        axisX.setLabelsFont(labelFont)
        axisY.setLabelsFont(labelFont)

        axisPen = QPen(Qt.white)
        axisPen.setWidth(2)

        axisX.setLinePen(axisPen)
        axisY.setLinePen(axisPen)   

        axixBrush = QBrush(Qt.white)
        axisX.setLabelsBrush(axixBrush)
        axisY.setLabelsBrush(axixBrush)

        axisX.append(['0-0.2', '0.2-0.4', '0.4-0.6', '0.6-0.8', '0.8-1.0'])
        axisX.setTitleText('axisX_title')

        axisY = QValueAxis()
        axisY.setRange(0, 100)
        axisY.setLabelFormat("%d")
        axisY.setTickCount(6)
        axisY.setTitleText('axisY_title')
        # add axis to chart
        # chart.addAxis(axisY, QtCore.Qt.AlignLeft)
        print(QCategoryAxis(axisX).labelsPosition())
        QCategoryAxis(axisX).setLabelsPosition(QCategoryAxis.AxisLabelsPositionOnValue)
        print(QCategoryAxis(axisX).labelsPosition())
        

        axisX.setGridLineVisible(True)
        axisY.setGridLineVisible(True)

        chart.addAxis(axisX, Qt.AlignBottom)
        chart.addAxis(axisY, Qt.AlignLeft)

        series.attachAxis(axisX)
        series.attachAxis(axisY)

        self.chartView = QChartView(chart)
        self.chartView.setRenderHint(QPainter.Antialiasing)

if __name__ == '__main__':
    app = QApplication(sys.argv)

    chartDemo = MyChart()
    chartDemo.show()

    sys.exit(app.exec_())

    