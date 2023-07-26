import os
import pickle
import cv2
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import QTableWidgetItem, QHeaderView, QLabel, QHBoxLayout, QDoubleSpinBox
from PyQt5 import QtCore, QtWidgets
from statistics import mean, mode, median, stdev, variance
import win32com.client as win32

# import openpyxl module
import openpyxl
# import BarChart class from openpyxl.chart sub_module
from openpyxl.chart import BarChart,Reference
import math
from datetime import datetime

from backend import database, chart, texts, algo_settings, logger

REPORTS_MAIN_PATH = 'reports'
CONTOURS_JSON_NAME = 'contours.pickle'
#
GRADING_PARAMS_JSON_NAME = 'grading_params.pickle'
CALIBRATION_COEFS_KEY = 'calib_coefs'
CIRCLE_ACC_THRS_KEY = 'circ_acc_thrs'
GRADING_RANGES_KEY = 'grading_ranges'
#


def save_report(report_id, contours_dict, px_values, circ_acc_thrs, ranges_dict):
    try:
        # check of root folder 
        report_path = os.path.join(REPORTS_MAIN_PATH, report_id)
        if not os.path.exists(report_path):
            os.mkdir(report_path)

        with open(os.path.join(report_path, CONTOURS_JSON_NAME), 'wb') as handle:
            pickle.dump(contours_dict, handle, protocol=pickle.HIGHEST_PROTOCOL)
        handle.close()
        
        # grading params
        grading_params = {CALIBRATION_COEFS_KEY: px_values,
                            CIRCLE_ACC_THRS_KEY: circ_acc_thrs,
                            GRADING_RANGES_KEY: ranges_dict}

        with open(os.path.join(report_path, GRADING_PARAMS_JSON_NAME), 'wb') as handle:
            pickle.dump(grading_params, handle, protocol=pickle.HIGHEST_PROTOCOL)
        handle.close()
    
    except:
        return


def get_filtered_reports_by_name(ui_obj, all_reports):
    filtered_reports = []
    # filter by name of report
    rep_id = ui_obj.search_text.text()
    for report in all_reports:
        if report[database.REPORTS_ID] == rep_id:
            filtered_reports.append(report)
    return filtered_reports

def get_filtered_reports_by_grading_range(ui_obj, all_reports):
    filtered_reports = []
    selected_range = []
    rep_id = ui_obj.report_range_combo.currentText()
    for report in all_reports:
        # filter by description
        if report[database.REPORTS_GRADING_RANGES_DESCRIPTION] == rep_id:
            filtered_reports.append(report)

    res, ranges_list = ui_obj.db.retrive_all(table_name=database.RANGES_TABLE_NAME)
    if not res:
        return
    else:
        for item in ranges_list:
            if item[database.RANGES_DESCRIPTION] == rep_id:
                selected_range = item[database.RANGES_RANGES]

    return filtered_reports, selected_range


def update_range_combobox_on_report_page(ui_obj):

    ##### clear combobox
    ui_obj.report_range_combo.clear()

    ##### get list of all defined ranges from ranges table
    list_of_ranges = algo_settings.get_list_of_defined_ranges(ui_obj)

    ##### add to combobox
    ui_obj.report_range_combo.addItems(list_of_ranges)

    ##### get the ranges
    res, ranges_list = ui_obj.db.retrive_all(table_name=database.RANGES_TABLE_NAME)
    
    if not res:
        return
    else:
        for item in ranges_list:
            if item[database.RANGES_IS_DEFAULT] == 'True':
                ###### find the default and set as combobox default
                ui_obj.report_range_combo.setCurrentIndex(ranges_list.index(item))

    #### add ranges to search area
    # add_ranges_to_search_feild_in_report(ranges_list, ui_obj)



def transform_string_range_to_dict(selected_range):
    ##### transform string of ranges to ranges one by one for table header
    string_headers = []
    if selected_range != [] and selected_range!='':
        string_headers = selected_range.split(',')
    return string_headers


def transform_string_percentages_to_float(string_float_array):

    ##### turn a string like '[1, 2, 3]' to [1.0, 2.0, 3.0]
    array_of_floats = []
    # 
    for number in string_float_array.split(','):
        if number[0]=='[':
            # remove begining [
            array_of_floats.append(round(float(number[1:].strip()), 3))
        elif number[-1] == ']':
            # remove ending ]
            array_of_floats.append(round(float(number[:-1].strip()), 3))
        else:
            # there's no bracket, just use the number with no whitespaces
            array_of_floats.append(round(float(number.strip()), 3))
    
    return array_of_floats
    



def add_ranges_to_search_feild_in_report(ranges_list, ui_obj):

    ##### clear the layouts
    for i in reversed(range(ui_obj.verticalLayout_ranges_report_search.count())): 
        ui_obj.verticalLayout_ranges_report_search.itemAt(i).widget().setParent(None)
        ui_obj.verticalLayout_lower_bound_report_search.itemAt(i).widget().setParent(None)
        ui_obj.verticalLayout_upper_bound_report_search.itemAt(i).widget().setParent(None)


    for index, item in enumerate(ranges_list):
        # print(item)
        item = ' < ' + item + ' < '
        ##### adding a label with the value of range to verticalLayout_ranges_report_search
        range_label_name = "ui_obj.range_label_in_report_page_" + str(index)
        exec(range_label_name  + "=QLabel(item)")
        exec("ui_obj.verticalLayout_ranges_report_search.addWidget("+range_label_name+")")

        ##### addspinbox for lowerbound
        lower_bound_spinbox_name = "ui_obj.lower_bound_spinbox_in_report_page_" + str(index)
        exec(lower_bound_spinbox_name  + "=QDoubleSpinBox(ui_obj)")
        exec(lower_bound_spinbox_name  +".setRange(0, 100)")
        exec("ui_obj.verticalLayout_lower_bound_report_search.addWidget("+lower_bound_spinbox_name+")")
 
        ##### add spinbox for upperbound
        upper_bound_spinbox_name = "ui_obj.upper_bound_spinbox_in_report_page_" + str(index)
        exec(upper_bound_spinbox_name  + "=QDoubleSpinBox(ui_obj)")
        exec(upper_bound_spinbox_name  +".setRange(0, 100)")
        exec(upper_bound_spinbox_name  +".setValue(100)")
        exec("ui_obj.verticalLayout_upper_bound_report_search.addWidget("+upper_bound_spinbox_name+")")


def search_reports_in_specific_date_range(start_date, end_date, all_reports, ui_obj):
    filtered_reports = []
    ######### turn dates to datetime obj to compare them
    start_date_datetime_obj = datetime.strptime(start_date, "%Y/%m/%d")
    end_date_datetime_obj =  datetime.strptime(end_date, "%Y/%m/%d")

    for report in all_reports:
        report_date = report[database.REPORTS_DATE]
        report_date_datatime_obj = datetime.strptime(report_date, "%Y/%m/%d")

        if start_date_datetime_obj <= report_date_datatime_obj <= end_date_datetime_obj:
            filtered_reports.append(report)

    if filtered_reports == []:
        ui_obj.show_message(label_name='label_report_search', text='no reports in selected date range', level=2, clearable=True)
        
    return filtered_reports


def search_reports_in_specific_range_percentages(all_reports, ui_obj, ranges_list):
    filtered_reports = []
    all_perecentages_in_range_flag = False
    for report in all_reports:
        report_percentages = transform_string_percentages_to_float(report[database.REPORTS_PERCENTAGES])
        for index, item in enumerate(ranges_list):
            lower_bound_spinbox_name = "ui_obj.lower_bound_spinbox_in_report_page_" + str(index)
            upper_bound_spinbox_name = "ui_obj.upper_bound_spinbox_in_report_page_" + str(index)
        
            lower_bound_value = eval('%s.value()' % (lower_bound_spinbox_name))
            upper_bound_value = eval('%s.value()' % (upper_bound_spinbox_name))
            # print('lower',lower_bound_value)
            # print('upper',upper_bound_value)
            # print('report_percentages',report_percentages[index])
            
            if lower_bound_value>upper_bound_value:
                #### check if lower bound and upperbound are correct
                ui_obj.show_message(label_name='label_report_search', text='percentage range is wrong in %s range'%(item), level=2, clearable=True)
                break

            if lower_bound_value <= report_percentages[index] <= upper_bound_value:
                #### pass
                all_perecentages_in_range_flag = True
            else:
                all_perecentages_in_range_flag = False
                break
        
        if all_perecentages_in_range_flag:
            filtered_reports.append(report)

    return filtered_reports




def filter_reports_by_date_and_ranges(ui_obj, all_reports, ranges_list):
    
    ################### filter by date ######################

    #### get selected dates from labels
    start_date = ui_obj.label_start_date_report_search.text()
    end_date = ui_obj.label_end_date_report_search.text()

    #### check if both are selected
    if (start_date == '' and end_date != '') or (start_date != '' and end_date == ''):
        ### one selected, other isnt
        ui_obj.show_message(label_name='label_report_search', text='start and dates are not selected correctly', level=1, clearable=True)
    
    elif start_date != '' and end_date != '':
        ### both dates are selected, filter reports
        ###check if start <= end date
        start_date_datetime_obj = datetime.strptime(start_date, "%Y/%m/%d")
        end_date_datetime_obj =  datetime.strptime(end_date, "%Y/%m/%d")
        if start_date_datetime_obj <= end_date_datetime_obj:
            ### dates passed, filter reports in range
            all_reports = search_reports_in_specific_date_range(start_date=start_date, end_date=end_date, all_reports=all_reports, ui_obj=ui_obj)
        else:
            ui_obj.show_message(label_name='label_report_search', text='start date is bigger than end date', level=2, clearable=True)

    ############## filter by range #####################
    all_reports = search_reports_in_specific_range_percentages(all_reports=all_reports, ui_obj=ui_obj, ranges_list=ranges_list)



    return all_reports



def load_reports_from_db_to_ui(ui_obj, filter_by_name=False, default_changed=False, filter_by_date_and_range=False, update_range_feilds=True, refresh_flag=True):

    # get repots from table of reports in db
    res, reports_list = ui_obj.db.retrive_all(table_name=database.REPORTS_TABLE_NAME)
    # print('len report list: ', len(reports_list))
    if not res:
        return
    
    ##### set default range if it is not changed in combobox
    if not default_changed:
        update_range_combobox_on_report_page(ui_obj)
        
    ##### filter reports by the chosen grading range from combobox
    reports_list, selected_range = get_filtered_reports_by_grading_range(ui_obj=ui_obj, all_reports=reports_list)
    # print('selected range: ', selected_range)

    # filter reports if needed
    if filter_by_name:
        reports_list = get_filtered_reports_by_name(ui_obj=ui_obj, all_reports=reports_list)
    
    ##### to select one exclusive report from table
    try:
        ui_obj.record_table.itemChanged.disconnect(ui_obj.table_item_checked)
    except:
        pass
    ui_obj.record_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)

    if refresh_flag:
        ##### refresh the date feilds
        ui_obj.label_start_date_report_search.clear()
        ui_obj.label_end_date_report_search.clear()

    ##### trun the string of selected to range to a float array
    ranges_dict = transform_string_range_to_dict(selected_range)  
    
    if update_range_feilds:
        ##### add selected ranges to report seach and filter feilds
        add_ranges_to_search_feild_in_report(ranges_dict, ui_obj)

    ##### filter by date and range
    if filter_by_date_and_range:
        reports_list = filter_reports_by_date_and_ranges(ui_obj=ui_obj, all_reports=reports_list, ranges_list = ranges_dict)
    # for report in reports_list:
        # print (report)
    ##### set four columns of selections, ID, date, time + number of ranges
    ui_obj.record_table.setColumnCount( 4 + len(ranges_dict))
    table_headres = [' ','ID', 'Date', 'Time'] + ranges_dict
    ui_obj.record_table.setHorizontalHeaderLabels(table_headres)

    ##### set enough rows for the filtered reports
    try:
        if len(reports_list) != 0:
            ui_obj.record_table.setRowCount(len(reports_list))
        else:
            ui_obj.record_table.setRowCount(0)
    except Exception as e:
        print(e)
    ##### go through chosen reports and put them in table
    for row, array_item in enumerate(reports_list):
        # set checkbox selector
        table_item = QTableWidgetItem()
        table_item.setTextAlignment(QtCore.Qt.AlignCenter)
        table_item.setFlags(QtCore.Qt.ItemFlag.ItemIsUserCheckable | QtCore.Qt.ItemFlag.ItemIsEnabled)
        table_item.setCheckState(QtCore.Qt.CheckState.Unchecked)
        ui_obj.record_table.setItem(row, 0, table_item)
        
        # set report id 
        table_item = QTableWidgetItem(str(array_item[database.REPORTS_ID]))
        table_item.setTextAlignment(QtCore.Qt.AlignCenter)
        ui_obj.record_table.setItem(row, 1, table_item)

        # set report date
        table_item = QTableWidgetItem(str(array_item[database.REPORTS_DATE]))
        table_item.setTextAlignment(QtCore.Qt.AlignCenter)
        ui_obj.record_table.setItem(row, 2, table_item)

        # set report time
        table_item = QTableWidgetItem(str(array_item[database.REPORTS_TIME]))
        table_item.setTextAlignment(QtCore.Qt.AlignCenter)
        ui_obj.record_table.setItem(row, 3, table_item)

        # percentage in each range
        percentages = transform_string_percentages_to_float(array_item[database.REPORTS_PERCENTAGES])
        for col, item in enumerate(percentages):
            table_item = QTableWidgetItem(str(item) + '%')
            table_item.setTextAlignment(QtCore.Qt.AlignCenter)
            ui_obj.record_table.setItem(row, col+4, table_item)

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

    res = ui_obj.report_manager.load_grading_info()
    if not res:
        ui_obj.show_message(label_name=ui_obj.label_report_search, text='error opening the file', level=2, clearable=True)
        return

    ui_obj.report_manager.show_report_details(report_id=selected_id)

    # update ui charts and items
    chart.create_ranges_chart_on_ui_report(ui_obj=ui_obj, grading_ranges=ui_obj.report_manager.grading_ranges)
    chart.create_circularity_chart_on_ui_report(ui_obj=ui_obj, axisX_title='Circularity', axisY_title='Percentage')
    chart.update_chart_reports(ui_obj=ui_obj, grading_params=ui_obj.report_manager.grading_ranges_arr, circ_acc=ui_obj.report_manager.circ_acc_array)
    algo_settings.update_percentages_on_report_page(ui_obj, ui_obj.report_manager.grading_ranges.values(), ui_obj.report_manager.grading_ranges_arr, ui_obj.report_manager.circ_acc_array)
    ui_obj.n_detected_objects_label_rep_2.setText(str(ui_obj.report_manager.n_objects))

    if len(ui_obj.report_manager.sizes_list)>3:
        ui_obj.mean_label.setText(str(round(mean(ui_obj.report_manager.sizes_list), 2)))
        ui_obj.mode_label.setText(str(round(mode(ui_obj.report_manager.sizes_list), 2)))
        # ui_obj.median_label.setText(str(round(median(ui_obj.report_manager.sizes_list), 2)))
        ui_obj.std_label.setText(str(round(stdev(ui_obj.report_manager.sizes_list), 2)))
        
    else:
        ui_obj.mean_label.setText(str('-'))
        ui_obj.mode_label.setText(str('-'))
        # ui_obj.median_label.setText(str('-'))
        ui_obj.std_label.setText(str('-'))
    
    # change stackwidget page to details
    ui_obj.stackedWidget_rep.setCurrentWidget(ui_obj.reports_detail_page)

    # show pdf and cdf plots
    count, bins_count = np.histogram(np.array(ui_obj.report_manager.sizes_list), bins=500)
    pdf = count / sum(count)
    cdf = np.cumsum(pdf)
    
    sc = chart.MplCanvas(width=5, height=1, dpi=140)
    # sc.axes.plot(bins_count[1:], pdf, color="red", label="PDF")
    sc.axes.plot(bins_count[1:], cdf, label="CDF")
    sc.axes.set_xlabel("(mm)")
    sc.axes.legend()
    chart.deleteLayout(ui_obj=ui_obj, layout=ui_obj.cumulative_chart_rep_fram.layout())
    hbox = QtWidgets.QVBoxLayout()
    hbox.addWidget(sc)
    ui_obj.cumulative_chart_rep_fram.setLayout(hbox)
    ui_obj.cumulative_chart_rep_fram.layout().setContentsMargins(0, 0, 0, 0)
    


def report_export_excel(ui_obj):
    
    # grading headers
    headers_grading = [str(value) for value in ui_obj.report_manager.grading_ranges.values()]
    # grading details
    grading_info = list(ui_obj.report_manager.grading_ranges_arr)
    gradinginfo_df = pd.DataFrame(data=grading_info, index=headers_grading, columns=['grading ranges'])
    # circle acc
    headers_circle_acc = ["(0-0.2)", "(0.2-0.4)", "(0.4-0.6)", "(0.6-0.8)", "(0.8-1.0)"]
    circularity_info = list(ui_obj.report_manager.circ_acc_array)
    circularity_info_df =  pd.DataFrame(data=circularity_info, index=headers_circle_acc,columns=['circularity percentage'])
    # statistical info of report
    headers_ither = ['n objects', 'mean', 'mode', 'STD']
    other_info = [ui_obj.report_manager.n_objects,
                    round(mean(ui_obj.report_manager.sizes_list), 3),
                    round(mode(ui_obj.report_manager.sizes_list), 3),
                    round(stdev(ui_obj.report_manager.sizes_list), 3)]

    other_info_df = pd.DataFrame(data=other_info, index=headers_ither, columns=['statistical information'])

    ##### get file path to save the file
    options = QtWidgets.QFileDialog.Options()
    csv_file_path, _ = QtWidgets.QFileDialog.getSaveFileName(ui_obj, caption='export excel', directory='./', filter="Excel Workbook(*.xlsx)", options=options)

    # save as excel
    if csv_file_path:
        try:
            with pd.ExcelWriter(csv_file_path, engine='xlsxwriter') as writer:
                gradinginfo_df.to_excel(writer, sheet_name='Sheet1', startrow=2, startcol=1)
                circularity_info_df.to_excel(writer, sheet_name='Sheet1', startrow=2, startcol=3)
                other_info_df.to_excel(writer, sheet_name='Sheet1', startrow=2, startcol=5)

        except Exception as e:
            print(e)
            print('error saving reports as excel')
    
    
    ##### draw charts in report excel file
    #Open an xlsx for reading
    try:
        wb2 = openpyxl.load_workbook(filename=csv_file_path)
    except:
        print('error opening the excel file')
        return
    #Get the current Active Sheet
    sheet = wb2.get_sheet_by_name("Sheet1")

    #### add dorsa logo
    img = openpyxl.drawing.image.Image('./Icons/dorsa13.png')
    img.width = 50
    img.height = 20
    sheet.add_image(img, "A1")

    #### report id
    sheet['B1'] = 'Report Id: '
    sheet['C1'] = str(ui_obj.report_manager.report_id)

    #### get date and time of report
    res, reports_list = ui_obj.db.retrive_all(table_name=database.REPORTS_TABLE_NAME)
    if not res:
        return
    for report in reports_list:
        if report[database.REPORTS_ID] == ui_obj.report_manager.report_id:
            date = report[database.REPORTS_DATE]
            time = report[database.REPORTS_TIME]

    sheet['D1'] = 'Date: '
    sheet['E1'] = date
    sheet['F1'] = 'Time: '
    sheet['G1'] = time

    # create data for plotting
    ####### refrence rows and columns where data and its labels are located
    values_grading_ranges = Reference(sheet, min_col = 3, min_row = 4, max_row = len(gradinginfo_df)+3)
    values_circularity_ranges = Reference(sheet, min_col = 5, min_row = 4, max_row = 8)
    
    labels_grading_ranges = Reference(sheet, min_col = 2, min_row = 4, max_row =len(gradinginfo_df)+3)
    labels_circularity_ranges = Reference(sheet, min_col = 4, min_row = 4, max_row = 8)


    # Create object of BarChart class
    chart_grading_ranges = BarChart()
    chart_circularity_ranges = BarChart()

    # adding data to the Bar chart object
    chart_grading_ranges.add_data(values_grading_ranges)
    chart_circularity_ranges.add_data(values_circularity_ranges)

    # set the title of the chart
    chart_grading_ranges.title = " grading ranges "
    chart_circularity_ranges.title = " circularity ranges "
    
    # set the title of the x-axis
    chart_grading_ranges.x_axis.title = " grading ranges "
    chart_circularity_ranges.x_axis.title = " circularity ranges "

    # set ranges of granulation and circularity
    chart_grading_ranges.set_categories(labels_grading_ranges)
    chart_circularity_ranges.set_categories(labels_circularity_ranges)
    
    
    # set the title of the y-axis
    chart_grading_ranges.y_axis.title = " percentage "
    chart_circularity_ranges.y_axis.title = " percentage "
    
    # add chart to the sheet
    # the buttom of screen
    # is anchored to cell B15 and B32.
    sheet.add_chart(chart_grading_ranges, "B15")
    sheet.add_chart(chart_circularity_ranges, "B32")
    
    ##### add CDF and PDF charts in excel
    # show pdf and cdf plots
    count, bins_count = np.histogram(np.array(ui_obj.report_manager.sizes_list), bins=500)
    pdf = count / sum(count)
    cdf = np.cumsum(pdf)
    
    # plt.plot(bins_count[1:], pdf, color="red", label="PDF")
    plt.plot(bins_count[1:], cdf, label="CDF")
    plt.xlabel('(mm)')

    plt.legend()
    plt.savefig("temp.png", dpi = 150)
    img = openpyxl.drawing.image.Image('temp.png')
    img.width = 500
    img.height = 300
    sheet.add_image(img, "B49")

    # save the file
    wb2.save(csv_file_path)

    ### make datas in excel autofit to cells
    # excel = win32.dynamic.Dispatch('Excel.Application')
    # wb = excel.Workbooks.Open(csv_file_path)
    # ws = wb.Worksheets("Sheet1")
    # ws.Columns.AutoFit()
    # wb.Save()
    # excel.Application.Quit()


def apply_to_delete_record(ui_obj):

    #### delete a record from reports table
    button_answer = ui_obj.show_alert_window(title=texts.TITLES['error'][ui_obj.language], message=texts.WARNINGS['are_you_sure_delete'][ui_obj.language], need_confirm=True)
    if button_answer == True:
            delete_report(ui_obj=ui_obj)


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


    def load_grading_info(self):
        # contours dict
        try:
            with open(os.path.join(self.report_path, CONTOURS_JSON_NAME), 'rb') as handle:
                self.contours_dict = pickle.load(handle)
            handle.close()

            with open(os.path.join(self.report_path, GRADING_PARAMS_JSON_NAME), 'rb') as handle:
                    grading_params = pickle.load(handle)
            handle.close()
        except:
            print('error while getting pickle of report')
            return False
        
        self.calib_coefs = grading_params[CALIBRATION_COEFS_KEY]
        self.circ_acc_thrs = grading_params[CIRCLE_ACC_THRS_KEY]
        self.grading_ranges = grading_params[GRADING_RANGES_KEY]
        self.n_objects = 0
        self.grading_ranges_arr = np.zeros((len(self.grading_ranges.keys())))
        self.sizes_list = []
        self.circ_acc_array = np.array([0]*5)

        # print('grading ranges (report)', self.grading_ranges)

        return True
        

    def show_report_details(self, report_id):
        ################# calculating the measures again ########################
        # # grading
        for cnts in self.contours_dict.values():
            # counter = 0
            for cnt in cnts:
                # counter = counter + 1
                
                # get contour cordinates
                (x1,y1), r = cv2.minEnclosingCircle(cnt)
                x, y, w, h = cv2.boundingRect(cnt)
                area = cv2.contourArea(cnt)

                # get r
                radius = min(w, h, r)
                ################## pixel to mm transform
                px_value = (self.calib_coefs[0]*x1 + self.calib_coefs[1]*y1 + self.calib_coefs[2]) * 0.92
                
                #### diameter
                radius_mm = (radius * px_value)*2 

                ###### find radious of equivalent circle
                ###### milimeter area of countour
                area_mm = area *  px_value *  px_value
                # print("milimeter area", area_mm)
                circle_equivalent_r = math.sqrt(area_mm/np.pi)
                # print("circle_equivalent_r", circle_equivalent_r)
                squre_mm = self.volume_of_cuntour(circle_equivalent_r, circle_equivalent_r)

                
                # reject those object that arent circular enoug or have size not in desired range
                if area / (np.pi * (radius) * (radius)) < self.circ_acc_thrs or not (self.grading_ranges[0][0]<=radius_mm<self.grading_ranges[len(self.grading_ranges.keys())-1][1]):
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
                    
                self.sizes_list.append(squre_mm)

        #         # update count
                self.n_objects+=1

        #         # grading
        #         for key in self.grading_ranges.keys():
        #             if self.grading_ranges[key][0] <= radius_mm < self.grading_ranges[key][1]:
        #                 # add tp grading arr
        #                 self.grading_ranges_arr[key]+=squre_mm
                        
            if  self.circ_acc_array.sum()!=0:
                self.circ_acc_array = (self.circ_acc_array / self.circ_acc_array.sum()) * 100
        #     if self.grading_ranges_arr.sum() != 0:
        #         self.grading_ranges_arr = (self.grading_ranges_arr / self.grading_ranges_arr.sum()) * 100

        # self.grading_ranges_arr = []
        res, reports_list = self.ui_obj.db.retrive_all(table_name=database.REPORTS_TABLE_NAME)
        if not res:
            return

        for report in reports_list:
            if report[database.REPORTS_ID] == report_id:
                report_percentages_float = transform_string_percentages_to_float(report[database.REPORTS_PERCENTAGES])
                # print('report_percentages_float: ', report_percentages_float)
                for index, item in enumerate(report_percentages_float):
                    self.grading_ranges_arr[index] = float(item)
                    # print(self.grading_ranges_arr)

   
    def volume_of_cuntour(self, w, h):
            vol = (4/3) * np.pi * (w*w*w)
            return vol