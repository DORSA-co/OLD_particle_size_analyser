import os
import pickle
import cv2
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import QTableWidgetItem, QHeaderView
from PyQt5 import QtCore, QtWidgets
from statistics import mean, mode, median, stdev, variance
from backend import database, chart

REPORTS_MAIN_PATH = 'reports'
CONTOURS_JSON_NAME = 'contours.pickle'
#
GRADING_PARAMS_JSON_NAME = 'grading_params.pickle'
CALIBRATION_COEFS_KEY = 'calib_coefs'
CIRCLE_ACC_THRS_KEY = 'circ_acc_thrs'
GRADING_RANGES_KEY = 'grading_ranges'
#
GRADING_BY_RMIN = 'by_rmin'
GRADING_BY_RMAX = 'by_rmax'
GRADING_BY_DIAMETER = 'by_diameter'
GRADING_BY_AREA = 'by_area'
GRADING_BY_VOLUME = 'by_volume'



def save_report(report_id, contours_dict, px_values, circ_acc_thrs, ranges_dict):
    try:
        # check of root folder wxi(sts
        report_path = os.path.join(REPORTS_MAIN_PATH, report_id)
        if not os.path.exists(report_path):
            os.mkdir(report_path)

        with open(os.path.join(report_path, CONTOURS_JSON_NAME), 'wb') as handle:
            pickle.dump(contours_dict, handle, protocol=pickle.HIGHEST_PROTOCOL)
        
        # grading params
        grading_params = {CALIBRATION_COEFS_KEY: px_values,
                            CIRCLE_ACC_THRS_KEY: circ_acc_thrs,
                            GRADING_RANGES_KEY: ranges_dict}

        with open(os.path.join(report_path, GRADING_PARAMS_JSON_NAME), 'wb') as handle:
            pickle.dump(grading_params, handle, protocol=pickle.HIGHEST_PROTOCOL)
    
    except:
        return


def get_filtered_reports(ui_obj, all_reports):
    filtered_reports = []
    # get filters
    rep_id = ui_obj.search_text.text()

    for report in all_reports:
        # filter by id
        if report[database.REPORTS_ID] == rep_id:
            filtered_reports.append(report)
    
    return filtered_reports

    
def load_reports_from_db_to_ui(ui_obj, filter=False):
    # get reprots from table
    res, reports_list = ui_obj.db.retrive_all(table_name=database.REPORTS_TABLE_NAME)
    if not res:
        return
    
    # filter reports if needed
    if filter:
        reports_list = get_filtered_reports(ui_obj=ui_obj, all_reports=reports_list)

    # set reports to table in ui
    # definr table parameters
    # ui_obj.record_table.resizeColumnsToContents()
    try:
        ui_obj.record_table.itemChanged.disconnect(ui_obj.table_item_checked)
    except:
        pass
    ui_obj.record_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
    # ui_obj.record_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
    
    if len(reports_list) != 0:
        ui_obj.record_table.setRowCount(len(reports_list))
    else:
        ui_obj.record_table.setRowCount(0)

    # add users to table
    for i, report in enumerate(reports_list):
        # set checkbox selector
        table_item = QTableWidgetItem()
        table_item.setTextAlignment(QtCore.Qt.AlignCenter)
        table_item.setFlags(QtCore.Qt.ItemFlag.ItemIsUserCheckable | QtCore.Qt.ItemFlag.ItemIsEnabled)
        table_item.setCheckState(QtCore.Qt.CheckState.Unchecked)
        ui_obj.record_table.setItem(i, 0, table_item)
        
        # set report id 
        table_item = QTableWidgetItem(str(report[database.REPORTS_ID]))
        # table_item.setTextAlignment(sQtCore.Qt.AlignCenter)
        ui_obj.record_table.setItem(i, 1, table_item)

        # set report date
        table_item = QTableWidgetItem(str(report[database.REPORTS_DATE]))
        # table_item.setTextAlignment(sQtCore.Qt.AlignCenter)
        ui_obj.record_table.setItem(i, 2, table_item)

        # set report time
        table_item = QTableWidgetItem(str(report[database.REPORTS_TIME]))
        table_item.setTextAlignment(QtCore.Qt.AlignCenter)
        ui_obj.record_table.setItem(i, 3, table_item)

        # set report grading ranges
        table_item = QTableWidgetItem(str(report[database.REPORTS_GRADING_RANGES]))
        table_item.setTextAlignment(QtCore.Qt.AlignCenter)
        ui_obj.record_table.setItem(i, 4, table_item)

        # set report save path
        table_item = QTableWidgetItem(str(report[database.REPORTS_SAVE_PATH]))
        table_item.setTextAlignment(QtCore.Qt.AlignCenter)
        ui_obj.record_table.setItem(i, 5, table_item)
    
    ui_obj.record_table.itemChanged.connect(ui_obj.table_item_checked)


def report_show_details(ui_obj):
    # get selected report in ui table
    selected_id = -1
    for i in range(ui_obj.record_table.rowCount()):    
        if ui_obj.record_table.item(i, 0).checkState() == QtCore.Qt.Checked:
            selected_id = ui_obj.record_table.item(i, 1).text()
            break
    
    if selected_id == -1:
        return
    
    # load report details
    ui_obj.report_manager.add_new_report(report_id=selected_id)
    ui_obj.report_manager.load_grading_info()
    ui_obj.report_manager.show_report_details()

    # update ui charts and items
    chart.create_ranges_chart_on_ui_report(ui_obj=ui_obj, grading_ranges=ui_obj.report_manager.grading_ranges)
    chart.create_circularity_chart_on_ui_report(ui_obj=ui_obj, axisX_title='Circularity', axisY_title='Percentage')
    chart.update_chart_reports(ui_obj=ui_obj, grading_params=ui_obj.report_manager.grading_ranges_arr, circ_acc=ui_obj.report_manager.circ_acc_array)
    
    
    ui_obj.n_detected_objects_label_rep_2.setText(str(ui_obj.report_manager.n_objects))

    if len(ui_obj.report_manager.sizes_list)>3:
        ui_obj.mean_label.setText(str(round(mean(ui_obj.report_manager.sizes_list), 3)))
        ui_obj.mode_label.setText(str(round(mode(ui_obj.report_manager.sizes_list), 3)))
        ui_obj.median_label.setText(str(round(median(ui_obj.report_manager.sizes_list), 3)))
        ui_obj.std_label.setText(str(round(stdev(ui_obj.report_manager.sizes_list), 3)))
        ui_obj.var_label.setText(str(round(variance(ui_obj.report_manager.sizes_list), 3)))
    else:
        ui_obj.mean_label.setText(str('-'))
        ui_obj.mode_label.setText(str('-'))
        ui_obj.median_label.setText(str('-'))
        ui_obj.std_label.setText(str('-'))
        ui_obj.var_label.setText(str('-'))
    
    # change stackwidget page to details
    ui_obj.stackedWidget_rep.setCurrentWidget(ui_obj.reports_detail_page)

    #
    # show pdf and cdf plots
    count, bins_count = np.histogram(np.array(ui_obj.report_manager.sizes_list), bins=500)
    pdf = count / sum(count)
    cdf = np.cumsum(pdf)
    
    sc = chart.MplCanvas(width=5, height=2, dpi=100)
    sc.axes.plot(bins_count[1:], pdf, color="red", label="PDF")
    sc.axes.plot(bins_count[1:], cdf, label="CDF")
    sc.axes.legend()
    chart.deleteLayout(ui_obj=ui_obj, layout=ui_obj.cumulative_chart_rep_fram.layout())
    hbox = QtWidgets.QVBoxLayout()
    hbox.addWidget(sc)
    ui_obj.cumulative_chart_rep_fram.setLayout(hbox)
    ui_obj.cumulative_chart_rep_fram.layout().setContentsMargins(0, 0, 0, 0)

    # plt.plot(bins_count[1:], pdf, color="red", label="PDF")
    # plt.plot(bins_count[1:], cdf, label="CDF")
    # plt.legend()
    # plt.show()
    # print(sizes)
    # plt.plot(norm.pdf(array,m,s))

    # pdf = sizes / (np.sum(sizes))
    # cdf = np.cumsum(pdf)
    # plt.plot(x, y, label="pdf")
    # plt.plot(x, cdf, label="cdf")
    # plt.xlabel("X")
    # plt.ylabel("Probability Values")
    # plt.title("CDF for continuous distribution")
    # plt.legend()
    # plt.show()
    

    # getting data of the histogram
    # count, bins_count = np.histogram(np.array(ui_obj.report_manager.sizes_list), bins=10)
    
    # # finding the PDF of the histogram using count values
    # pdf = count / sum(count)
    
    # # using numpy np.cumsum to calculate the CDF
    # # We can also find using the PDF values by looping and adding
    # cdf = np.cumsum(pdf)
    
    # # plotting PDF and CDF
    # plt.plot(bins_count[1:], pdf, color="red", label="PDF")
    # plt.plot(bins_count[1:], cdf, label="CDF")
    # plt.legend()
    # plt.show()


def report_export_excel(ui_obj):
    # grading
    headers_grading = [str(value) for value in ui_obj.report_manager.grading_ranges.values()]
    print(headers_grading)
    grading_info = list(ui_obj.report_manager.grading_ranges_arr)
    print(grading_info)
    gradinginfo_df = pd.DataFrame(data={key: [value] for key, value in zip(headers_grading, grading_info)})

    # circle acc
    headers_circle_acc = ['0-0.2', '0.2-0.4', '0.4-0.6', '0.6-0.8', '0.8-1.0']
    circularity_info = list(ui_obj.report_manager.circ_acc_array)
    circularity_info_df = pd.DataFrame(data={key: [value] for key, value in zip(headers_circle_acc, circularity_info)})

    # other info
    headers_ither = ['n objects', 'mean', 'mode', 'median', 'standard deviation', 'variance']
    other_info = [ui_obj.report_manager.n_objects,
                    round(mean(ui_obj.report_manager.sizes_list), 3),
                    round(mode(ui_obj.report_manager.sizes_list), 3),
                    round(median(ui_obj.report_manager.sizes_list), 3),
                    round(stdev(ui_obj.report_manager.sizes_list), 3),
                    round(variance(ui_obj.report_manager.sizes_list), 3)]

    other_info_df = pd.DataFrame(data={key: [value] for key, value in zip(headers_ither, other_info)})

    

    options = QtWidgets.QFileDialog.Options()
    csv_file_path, _ = QtWidgets.QFileDialog.getSaveFileName(ui_obj, caption='export excel', directory='./', filter="Excel Workbook(*.xlsx)", options=options)

    # save as excel
    if csv_file_path:
        try:
            with pd.ExcelWriter(csv_file_path, engine='xlsxwriter') as writer:
                gradinginfo_df.to_excel(writer, sheet_name='Sheet1', startrow=1, startcol=1)
                circularity_info_df.to_excel(writer, sheet_name='Sheet1', startrow=len(gradinginfo_df)+4, startcol=1)
                other_info_df.to_excel(writer, sheet_name='Sheet1', startrow=len(gradinginfo_df)+8, startcol=1)

        except Exception as e:
            print(e)
            print('error saving reports as excel')


def delete_report(ui_obj):
    # get selected report in ui table
    selected_id = -1
    for i in range(ui_obj.record_table.rowCount()):    
        if ui_obj.record_table.item(i, 0).checkState() == QtCore.Qt.Checked:
            selected_id = ui_obj.record_table.item(i, 1).text()
            break
    
    if selected_id == -1:
        return
    
    # delete record
    ui_obj.db.remove_record(col_name=database.REPORTS_ID, id=selected_id, table_name=database.REPORTS_TABLE_NAME)
    
    # refresh table
    load_reports_from_db_to_ui(ui_obj=ui_obj)

    


class Report_Manager():
    def __init__(self, ui_obj):
        self.ui_obj = ui_obj
    
    
    def add_new_report(self, report_id):
       
        #
        self.report_id = report_id
        self.contours_dict = None
        self.report_path = os.path.join(REPORTS_MAIN_PATH, report_id)
        #
        self.calib_coefs = None
        self.circ_acc_thrs = None
        self.grading_ranges = None
        #
        self.grading_by = 0
        self.get_grading_by_from_ui()
    

    def get_grading_by_from_ui(self):
        if self.ui_obj.rep_grading_by_dmin_radio.isChecked():
            self.grading_by = 0
        
        # elif self.ui_obj.rep_grading_by_dmax_radio.isChecked():
        #     self.grading_by = 1

        elif self.ui_obj.rep_grading_by_area_radio.isChecked():
            self.grading_by = 2

        elif self.ui_obj.rep_grading_by_volume_radio.isChecked():
            self.grading_by = 3
    

    def change_grading_ranges_acoarding_to_grading_basis(self):
        if self.grading_by==2:
            for key in self.grading_ranges.keys():
                self.grading_ranges[key][0] = round(((self.grading_ranges[key][0]/2)**2) * np.pi, 2)
                self.grading_ranges[key][1] = round(((self.grading_ranges[key][1]/2)**2) * np.pi, 2)

        if self.grading_by==3:
            for key in self.grading_ranges.keys():
                self.grading_ranges[key][0] = round(((self.grading_ranges[key][0]/2)**3) * np.pi * (4/3), 2)
                self.grading_ranges[key][1] = round(((self.grading_ranges[key][1]/2)**3) * np.pi * (4/3), 2)
    

    def load_grading_info(self):
        # contours dict
        with open(os.path.join(self.report_path, CONTOURS_JSON_NAME), 'rb') as handle:
            self.contours_dict = pickle.load(handle)

        # grading params
        with open(os.path.join(self.report_path, GRADING_PARAMS_JSON_NAME), 'rb') as handle:
            grading_params = pickle.load(handle)

        self.calib_coefs = grading_params[CALIBRATION_COEFS_KEY]
        self.circ_acc_thrs = grading_params[CIRCLE_ACC_THRS_KEY]

        self.grading_ranges = grading_params[GRADING_RANGES_KEY]
        self.change_grading_ranges_acoarding_to_grading_basis()

        self.n_objects = 0
        self.grading_ranges_arr = np.zeros((len(self.grading_ranges.keys())))
        self.sizes_list = []
        self.circ_acc_array = np.array([0]*5)

        print('grading ranges', self.grading_ranges)
        

    def show_report_details(self):
        # grading
        for cnts in self.contours_dict.values():
            for cnt in cnts:
                # get contour cordinates
                (x1,y1), r = cv2.minEnclosingCircle(cnt)
                x, y, w, h = cv2.boundingRect(cnt)
                area = cv2.contourArea(cnt)

                # get r
                # print(w, h, 2*r)
                if self.grading_by==0:
                    radius = min(w, h, 2*r)
                elif self.grading_by==1:
                    radius = max(w, h, 2*r)

                elif self.grading_by==2:
                    circ_area = (((max(w, h, 2*r) + min(w, h, 2*r))/4) ** 2) * np.pi
                    radius = (max(w, h, 2*r) + min(w, h, 2*r))/2
                elif self.grading_by==3:
                    circ_vol = (((max(w, h, 2*r) + min(w, h, 2*r))/4) ** 3) * np.pi * (4/3)
                    radius = (max(w, h, 2*r) + min(w, h, 2*r))/2

                px_value = self.calib_coefs[0]*x1 + self.calib_coefs[1]*y1 + self.calib_coefs[2]

                if self.grading_by<=1:
                    radius_mm = (radius * px_value)
                elif self.grading_by==2:
                    radius_mm = (circ_area * px_value)
                elif self.grading_by==3:
                    radius_mm = (circ_vol * px_value)

                
                # reject those object that arent circular enoug or have size not in desired range
                # print(area / (np.pi * (radius/2) * (radius/2)))
                if area / (np.pi * (radius/2) * (radius/2)) < self.circ_acc_thrs:
                    continue

                # circular acc
                circ_acc = min(w, h) / max(w, h)
                if 0 < circ_acc < 0.2:
                    self.circ_acc_array[0]+=1
                elif 0.2 <= circ_acc < 0.4:
                    self.circ_acc_array[1]+=1
                elif 0.4 <= circ_acc < 0.6:
                    self.circ_acc_array[2]+=1
                elif 0.6 <= circ_acc < 0.8:
                    self.circ_acc_array[3]+=1
                else:
                    self.circ_acc_array[4]+=1

                if not (self.grading_ranges[0][0]<=radius_mm<self.grading_ranges[len(self.grading_ranges.keys())-1][1]):
                    continue
                    
                

                

                # grading
                for key in self.grading_ranges.keys():
                    if self.grading_ranges[key][0] <= radius_mm < self.grading_ranges[key][1]:
                        # add to grading arr
                        self.grading_ranges_arr[key]+=1

                        # update count
                        self.n_objects+=1
                        self.sizes_list.append(radius_mm)

            if  self.circ_acc_array.sum()!=0:
                self.circ_acc_array = (self.circ_acc_array / self.circ_acc_array.sum()) * 100
                
        print('n obj: ', self.n_objects)
        self.grading_ranges_arr = (self.grading_ranges_arr / self.grading_ranges_arr.sum()) * 100
        print(self.grading_ranges_arr, self.circ_acc_array, self.n_objects)     