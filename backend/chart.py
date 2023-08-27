from PyQt5.QtChart import QChart, QBarSet, QBarSeries, QBarCategoryAxis, QValueAxis, QChartView
from PyQt5 import QtCore, QtGui, QtWidgets, sip
import math
#
import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure


def update_chart(ui_obj, grading_params, circ_acc):
    # check values not to be nan
    for param in grading_params:
        if math.isnan(param):
            return

    for i, param in enumerate(grading_params):
        ui_obj.ranges_barset.replace(i, round(param,2))
    
    for i, param in enumerate(circ_acc):
        ui_obj.circ_barset.replace(i, round(param,2))


def reset_chart(ui_obj):  
    # for i in range(len(ui_obj.algo_params.ranges_dict.keys())):
    #     ui_obj.ranges_barset.replace(i, 0)
    
    for i in range(5):
        ui_obj.circ_barset.replace(i, 0)


def update_chart_reports(ui_obj, grading_params, circ_acc):
    # check values not to be nan
    for param in grading_params:
        if math.isnan(param):
            return

    for i, param in enumerate(grading_params):
        ui_obj.report_ranges_barset.replace(i, round(param,2))
    
    for i, param in enumerate(circ_acc):
        ui_obj.circ_barset_report.replace(i, round(param,2))


def create_ranges_chart_on_ui(ui_obj, axisX_title='Grading Range (mm)', axisY_title='Percentage'):
    # clear layout
    deleteLayout(ui_obj=ui_obj, layout=ui_obj.grad_chart_fram.layout())

    #create barseries
    ui_obj.ranges_barset = QBarSet(axisX_title)

    #insert data to the barseries
    for _ in range(len(ui_obj.algo_params.ranges_dict.keys())):
        ui_obj.ranges_barset.append(0)
    
    #we want to create percent bar series
    ui_obj.series = QBarSeries()
    ui_obj.series.setLabelsVisible(True)
    ui_obj.series.append(ui_obj.ranges_barset)

    #create chart and add the series in the chart
    ui_obj.chart = QChart()
    ui_obj.chart.addSeries(ui_obj.series)
    ui_obj.chart.legend().setVisible(False)
    ui_obj.chart.setAnimationOptions(QChart.SeriesAnimations)
    ui_obj.chart.setTheme(QChart.ChartThemeDark)
    ui_obj.chart.setMargins(QtCore.QMargins(10, 10, 10, 10))
    
    # axisX
    axisX = QBarCategoryAxis()
    axisX.append(['%s-%s' % (range_[0], range_[1]) for range_ in ui_obj.algo_params.ranges_dict.values()])
    axisX.setTitleText(axisX_title)
    ui_obj.chart.setAxisX(axisX, ui_obj.series)

    # axisY
    axisY = QValueAxis()
    axisY.setRange(0, 100)
    axisY.setLabelFormat("%d")
    axisY.setTickCount(6)
    axisY.setTitleText(axisY_title)
    # add axis to chart
    ui_obj.chart.addAxis(axisY, QtCore.Qt.AlignLeft)

    # attach axis
    ui_obj.series.attachAxis(axisY)
    
    #create chartview and add the chart in the chartview
    chartview = QChartView(ui_obj.chart)
    chartview.setContentsMargins(10, 10, 10, 10)
    chartview.setRenderHint(QtGui.QPainter.Antialiasing)

    # define hbox layout
    hbox = QtWidgets.QVBoxLayout()
    hbox.addWidget(chartview)
    hbox.setContentsMargins(0, 0, 0, 0)
    # add to frame
    ui_obj.grad_chart_fram.setLayout(hbox)
    ui_obj.grad_chart_fram.layout().setContentsMargins(0, 0, 0, 0)


def create_ranges_chart_on_ui_report(ui_obj, grading_ranges, axisX_title='Grading Range (mm)', axisY_title='Percentage'):
    # clear layout
    deleteLayout(ui_obj=ui_obj, layout=ui_obj.grad_chart_rep_fram.layout())

    #create barseries
    ui_obj.report_ranges_barset = QBarSet(axisX_title)

    #insert data to the barseries
    for _ in range(len(grading_ranges.keys())):
        ui_obj.report_ranges_barset.append(0)
    
    #we want to create percent bar series
    ui_obj.report_series = QBarSeries()
    ui_obj.report_series.setLabelsVisible(True)
    ui_obj.report_series.append(ui_obj.report_ranges_barset)

    #create chart and add the series in the chart
    ui_obj.report_chart = QChart()
    ui_obj.report_chart.addSeries(ui_obj.report_series)
    ui_obj.report_chart.legend().setVisible(False)
    ui_obj.report_chart.setAnimationOptions(QChart.SeriesAnimations)
    ui_obj.report_chart.setTheme(QChart.ChartThemeDark)
    ui_obj.report_chart.setMargins(QtCore.QMargins(5, 5, 5, 5))
    
    # axisX
    axisX = QBarCategoryAxis()
    axisX.append(['%s-%s' % (range_[0], range_[1]) for range_ in grading_ranges.values()])
    axisX.setTitleText(axisX_title)
    ui_obj.report_chart.setAxisX(axisX, ui_obj.report_series)

    # axisY
    axisY = QValueAxis()
    axisY.setRange(0, 100)
    axisY.setLabelFormat("%d")
    axisY.setTickCount(6)
    axisY.setTitleText(axisY_title)
    # add axis to chart
    ui_obj.report_chart.addAxis(axisY, QtCore.Qt.AlignLeft)

    # attach axis
    ui_obj.report_series.attachAxis(axisY)
    
    #create chartview and add the chart in the chartview
    chartview = QChartView(ui_obj.report_chart)
    chartview.setContentsMargins(5, 5, 5, 5)
    chartview.setRenderHint(QtGui.QPainter.Antialiasing)

    # define hbox layout
    hbox = QtWidgets.QVBoxLayout()
    hbox.addWidget(chartview)
    hbox.setContentsMargins(5, 5, 5, 5)
    # add to frame
    ui_obj.grad_chart_rep_fram.setLayout(hbox)
    ui_obj.grad_chart_rep_fram.layout().setContentsMargins(0, 0, 0, 0)


def create_circularity_chart_on_ui(ui_obj, axisX_title='Circularity', axisY_title='Percentage'):
    # clear layout
    deleteLayout(ui_obj=ui_obj, layout=ui_obj.circle_chart_fram.layout())

    #create barseries
    ui_obj.circ_barset = QBarSet(axisX_title)

    #insert data to the barseries
    #insert data to the barseries
    for _ in range(5):
        ui_obj.circ_barset.append(0)
    
    #we want to create percent bar series
    ui_obj.circ_series = QBarSeries()
    ui_obj.circ_series.setLabelsVisible(True)
    ui_obj.circ_series.append(ui_obj.circ_barset)

    #create chart and add the series in the chart
    ui_obj.circ_chart = QChart()
    ui_obj.circ_chart.addSeries(ui_obj.circ_series)
    ui_obj.circ_chart.legend().setVisible(False)
    ui_obj.circ_chart.setAnimationOptions(QChart.SeriesAnimations)
    ui_obj.circ_chart.setTheme(QChart.ChartThemeDark)
    ui_obj.circ_chart.setMargins(QtCore.QMargins(5, 5, 15, 5))
    
    # axisX
    axisX = QBarCategoryAxis()
    axisX.append(['0-0.2', '0.2-0.4', '0.4-0.6', '0.6-0.8', '0.8-1.0'])
    axisX.setTitleText(axisX_title)
    ui_obj.circ_chart.setAxisX(axisX, ui_obj.circ_series)

    # axisY
    axisY = QValueAxis()
    axisY.setRange(0, 100)
    axisY.setLabelFormat("%d")
    axisY.setTickCount(6)
    axisY.setTitleText(axisY_title)
    # add axis to chart
    ui_obj.circ_chart.addAxis(axisY, QtCore.Qt.AlignLeft)

    # attach axis
    ui_obj.circ_series.attachAxis(axisY)
    
    #create chartview and add the chart in the chartview
    chartview = QChartView(ui_obj.circ_chart)
    chartview.setContentsMargins(5, 5, 5, 5)
    chartview.setRenderHint(QtGui.QPainter.Antialiasing)

    # define hbox layout
    hbox = QtWidgets.QVBoxLayout()
    hbox.addWidget(chartview)
    hbox.setContentsMargins(5, 5, 5, 5)
    # add to frame
    ui_obj.circle_chart_fram.setLayout(hbox)
    ui_obj.circle_chart_fram.layout().setContentsMargins(0, 0, 0, 0)



def create_circularity_chart_on_ui_report(ui_obj, axisX_title='Circularity', axisY_title='Percentage'):
    # clear layout
    deleteLayout(ui_obj=ui_obj, layout=ui_obj.circle_chart_rep_fram.layout())

    #create barseries
    ui_obj.circ_barset_report = QBarSet(axisX_title)

    #insert data to the barseries
    #insert data to the barseries
    for _ in range(5):
        ui_obj.circ_barset_report.append(0)
    
    #we want to create percent bar series
    ui_obj.circ_series_report = QBarSeries()
    ui_obj.circ_series_report.setLabelsVisible(True)
    ui_obj.circ_series_report.append(ui_obj.circ_barset_report)

    #create chart and add the series in the chart
    ui_obj.circ_chart_report = QChart()
    ui_obj.circ_chart_report.addSeries(ui_obj.circ_series_report)
    ui_obj.circ_chart_report.legend().setVisible(False)
    ui_obj.circ_chart_report.setAnimationOptions(QChart.SeriesAnimations)
    ui_obj.circ_chart_report.setTheme(QChart.ChartThemeDark)
    ui_obj.circ_chart_report.setMargins(QtCore.QMargins(5, 5, 15, 5))
    
    # axisX
    axisX = QBarCategoryAxis()
    axisX.append(['0-0.2', '0.2-0.4', '0.4-0.6', '0.6-0.8', '0.8-1.0'])
    axisX.setTitleText(axisX_title)
    ui_obj.circ_chart_report.setAxisX(axisX, ui_obj.circ_series_report)

    # axisY
    axisY = QValueAxis()
    axisY.setRange(0, 100)
    axisY.setLabelFormat("%d")
    axisY.setTickCount(6)
    axisY.setTitleText(axisY_title)
    # add axis to chart
    ui_obj.circ_chart_report.addAxis(axisY, QtCore.Qt.AlignLeft)

    # attach axis
    ui_obj.circ_series_report.attachAxis(axisY)
    
    #create chartview and add the chart in the chartview
    chartview = QChartView(ui_obj.circ_chart_report)
    chartview.setContentsMargins(5, 5, 5, 5)
    chartview.setRenderHint(QtGui.QPainter.Antialiasing)

    # define hbox layout
    hbox = QtWidgets.QVBoxLayout()
    hbox.addWidget(chartview)
    hbox.setContentsMargins(5, 5, 5, 5)
    # add to frame
    ui_obj.circle_chart_rep_fram.setLayout(hbox)
    ui_obj.circle_chart_rep_fram.layout().setContentsMargins(0, 0, 0, 0)


def deleteLayout(ui_obj, layout):
    if layout is not None:
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
            else:
                ui_obj.deleteLayout(item.layout())
        sip.delete(layout)



class MplCanvas(FigureCanvasQTAgg):
    # this class is used to create a matplotlib plot on gt gui

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super(MplCanvas, self).__init__(fig)

    
    

