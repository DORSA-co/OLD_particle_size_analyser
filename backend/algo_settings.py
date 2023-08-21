from backend import database , texts, reports
from PyQt5.QtWidgets import * #QTableWidgetItem, QHeaderView, QButtonGroup, QRadioButton, QLabel
from PyQt5 import QtCore, QtWidgets, QtGui
from mycolorpy import colorlist as mcp
from functools import partial

def load_algo_params_from_db_to_ui(ui_obj):
    # get algo params from table
    res, algo_params_list = ui_obj.db.retrive_all(table_name=database.ALGO_TABLE_NAME)
    if not res:
        return

    # set algorithm parameters to table in ui
    ui_obj.algo_param_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
    try:
        ui_obj.algo_param_table.itemChanged.disconnect(ui_obj.table_item_checked)
    except:
        pass
    
    if len(algo_params_list) != 0:
        ui_obj.algo_param_table.setRowCount(len(algo_params_list))
    else:
        ui_obj.algo_param_table.setRowCount(0)

    # add users to table
    for i, report in enumerate(algo_params_list):
        # set checkbox selector
        table_item = QTableWidgetItem()
        table_item.setTextAlignment(QtCore.Qt.AlignCenter)
        table_item.setFlags(QtCore.Qt.ItemFlag.ItemIsUserCheckable | QtCore.Qt.ItemFlag.ItemIsEnabled)
        table_item.setCheckState(QtCore.Qt.CheckState.Unchecked)
        ui_obj.algo_param_table.setItem(i, 0, table_item)
        # group = QButtonGroup(table_item)
        # for i, name in enumerate(colsNames):
        # button = QRadioButton()
        # group.addButton(button)
        # ui_obj.algo_param_table.setItem(i, 0, button)
        # button.setChecked(False)
      
        # set algorithm description
        table_item = QTableWidgetItem(str(report[database.ALGO_DESCRIPTION]))
        # table_item.setTextAlignment(sQtCore.Qt.AlignCenter)
        ui_obj.algo_param_table.setItem(i, 1, table_item)

        # set algorithm min circularity
        table_item = QTableWidgetItem(str(report[database.ALGO_MIN_CIRCULARITY]))
        # table_item.setTextAlignment(sQtCore.Qt.AlignCenter)
        ui_obj.algo_param_table.setItem(i, 2, table_item)

        # set algorithm blur ksize
        table_item = QTableWidgetItem(str(report[database.ALGO_BLUR_KSIZE]))
        table_item.setTextAlignment(QtCore.Qt.AlignCenter)
        ui_obj.algo_param_table.setItem(i, 3, table_item)

        # set algorithm gray threshold
        table_item = QTableWidgetItem(str(report[database.ALGO_GRAY_THRS]))
        table_item.setTextAlignment(QtCore.Qt.AlignCenter)
        ui_obj.algo_param_table.setItem(i, 4, table_item)

        # set algorithm is defalut
        table_item = QTableWidgetItem(str(report[database.ALGO_IS_DEFAULT]))
        table_item.setTextAlignment(QtCore.Qt.AlignCenter)
        ui_obj.algo_param_table.setItem(i, 5, table_item)
        if str(report[database.ALGO_IS_DEFAULT]) == "True":
            ui_obj.algo_param_table.item(i, 0).setCheckState(QtCore.Qt.Checked)

    add_selected_algo_params_to_ui(ui_obj=ui_obj, change_default_algo_=False)
    ui_obj.algo_param_table.itemChanged.connect(ui_obj.table_item_checked)
    


def get_algo_params_from_ui(ui_obj):
    algo_params = {}
    algo_params[database.ALGO_DESCRIPTION] = ui_obj.algo_desc_lineedit.text()
    blur_ksize = ui_obj.blur_ksize_spin_2.value()
    algo_params[database.ALGO_BLUR_KSIZE] = blur_ksize if blur_ksize%2==1 else blur_ksize+1
    algo_params[database.ALGO_GRAY_THRS] = ui_obj.gray_spin_2.value()
    circ_acc = ui_obj.circ_acc_spin_2.value()
    algo_params[database.ALGO_MIN_CIRCULARITY] = circ_acc #if circ_acc<=1 else circ_acc/100

    return algo_params


def set_algo_params_from_ui_to_db(ui_obj):
    # get from ui
    algo_params = get_algo_params_from_ui(ui_obj=ui_obj)
    if algo_params[database.ALGO_DESCRIPTION]=='':
        ui_obj.show_message(label_name='label_msg_range', text='description empty', level=2, clearable=True)
        return


    #### check if the description is redundant
    res, algo_params_list = ui_obj.db.retrive_all(table_name=database.ALGO_TABLE_NAME)
    if res:
        for i in range(len(algo_params_list)):
            if algo_params[database.ALGO_DESCRIPTION] == algo_params_list[i][database.ALGO_DESCRIPTION]:
                ui_obj.show_message(label_name='label_msg_range', text='description already been used', level=2, clearable=True)
                return

    # save to database
    ui_obj.db.add_record(data=[algo_params[database.ALGO_DESCRIPTION], algo_params[database.ALGO_BLUR_KSIZE], algo_params[database.ALGO_GRAY_THRS], algo_params[database.ALGO_MIN_CIRCULARITY], True], table_name=database.ALGO_TABLE_NAME, parametrs=[database.ALGO_DESCRIPTION,database.ALGO_BLUR_KSIZE, database.ALGO_GRAY_THRS, database.ALGO_MIN_CIRCULARITY, database.ALGO_IS_DEFAULT])
    
    # update default record
    change_default_algo(ui_obj=ui_obj, record_description=algo_params[database.ALGO_DESCRIPTION])

    # refresh table
    load_algo_params_from_db_to_ui(ui_obj=ui_obj)


def change_default_algo(ui_obj, record_description):
    # set all table cols default to false
    ui_obj.db.update_colomn_for_all_items(table_name=database.ALGO_TABLE_NAME, col_name=database.ALGO_IS_DEFAULT, value=False)

    # change selected algorithm to default
    ui_obj.db.update_column(table_name=database.ALGO_TABLE_NAME, searching_col_name=database.ALGO_DESCRIPTION, searching_value=record_description, col_name=database.ALGO_IS_DEFAULT, value=True)
    
    # refresh table
    load_algo_params_from_db_to_ui(ui_obj=ui_obj)


def apply_to_delete_range(ui_obj):
    button_answer = ui_obj.show_alert_window(title=texts.TITLES['error'][ui_obj.language], message=texts.WARNINGS['are_you_sure_delete'][ui_obj.language], need_confirm=True)
    if button_answer == True:
            delete_range(ui_obj=ui_obj)


def delete_algo(ui_obj):
    # get selected report in ui table
    selected_id = -1
    for i in range(ui_obj.algo_param_table.rowCount()):    
        if ui_obj.algo_param_table.item(i, 0).checkState() == QtCore.Qt.Checked:
            selected_id = ui_obj.algo_param_table.item(i, 1).text()
            break
    if selected_id == -1:
        return

    # delete record
    ui_obj.db.remove_record(col_name=database.ALGO_DESCRIPTION, id=selected_id, table_name=database.ALGO_TABLE_NAME)
    
    # refresh table
    load_algo_params_from_db_to_ui(ui_obj=ui_obj)


def get_list_of_defined_ranges(ui_obj):
    list_of_ranges = []
    ##### retrive ranges table
    res, ranges_list = ui_obj.db.retrive_all(table_name=database.RANGES_TABLE_NAME)
    if not res:
        return
    
    for item in ranges_list:
        list_of_ranges.append(str(item[database.RANGES_DESCRIPTION]))
    return list_of_ranges



# ---------------------------------------------------------------------
def load_ranges_from_db_to_ui(ui_obj):
    # get ranges from table
    res, ranges_list = ui_obj.db.retrive_all(table_name=database.RANGES_TABLE_NAME)
    if not res:
        return

    # set reports to table in ui
    # define table parameters
    # ui_obj.record_table.resizeColumnsToContents()
    ui_obj.ranges_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
    try:
        ui_obj.ranges_table.itemChanged.disconnect(ui_obj.table_item_checked)
    except:
        pass
    # ui_obj.record_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
    
    if len(ranges_list) != 0:
        ui_obj.ranges_table.setRowCount(len(ranges_list))
    else:
        ui_obj.ranges_table.setRowCount(0)

    # add users to table
    for i, range_ in enumerate(ranges_list):
        # set checkbox selector
        table_item = QTableWidgetItem()
        table_item.setTextAlignment(QtCore.Qt.AlignCenter)
        table_item.setFlags(QtCore.Qt.ItemFlag.ItemIsUserCheckable | QtCore.Qt.ItemFlag.ItemIsEnabled)
        table_item.setCheckState(QtCore.Qt.CheckState.Unchecked)
        ui_obj.ranges_table.setItem(i, 0, table_item)
        
        # set range id
        table_item = QTableWidgetItem(str(range_[database.RANGES_ID]))
        # table_item.setTextAlignment(sQtCore.Qt.AlignCenter)
        ui_obj.ranges_table.setItem(i, 1, table_item)

        # set range description
        table_item = QTableWidgetItem(str(range_[database.RANGES_DESCRIPTION]))
        # table_item.setTextAlignment(sQtCore.Qt.AlignCenter)
        ui_obj.ranges_table.setItem(i, 2, table_item)

        # set ranges
        table_item = QTableWidgetItem(str(range_[database.RANGES_RANGES]))
        # table_item.setTextAlignment(sQtCore.Qt.AlignCenter)
        ui_obj.ranges_table.setItem(i, 3, table_item)

        # set ia default
        table_item = QTableWidgetItem(str(range_[database.RANGES_IS_DEFAULT]))
        # table_item.setTextAlignment(sQtCore.Qt.AlignCenter)
        ui_obj.ranges_table.setItem(i, 4, table_item)
        if str(range_[database.RANGES_IS_DEFAULT]) == "True":
            ui_obj.ranges_table.item(i, 0).setCheckState(QtCore.Qt.Checked)

    add_selected_range_to_ui(ui_obj, change_default_range_=False)
    ui_obj.ranges_table.itemChanged.connect(ui_obj.table_item_checked)


def add_range_to_db(ui_obj, ranges_dict):
    # get range description from ui
    range_description = ui_obj.range_desc_lineedit.text()
    if range_description=='':
        ui_obj.show_message(label_name='label_msg_range', text='description empty', level=2, clearable=True)
        return

    # convert ranges dict values to a string
    range_string = ''
    for value in ranges_dict.values():
        range_string = range_string + '%s-%s' % (value[0], value[1]) + ','
    range_string = range_string[:-1]

    # add to db
    res, ranges_list = ui_obj.db.retrive_all(table_name=database.RANGES_TABLE_NAME)
    if not res:
        return
    else:
        for i in range(len(ranges_list)):
            if range_description == ranges_list[i][database.RANGES_DESCRIPTION]:
                ui_obj.show_message(label_name='label_msg_range', text='description already been used', level=2, clearable=True)
                return

    cur_idx = 0 if len(ranges_list)==0 else ranges_list[-1][database.RANGES_ID]
    ui_obj.db.add_record(data=[int(cur_idx)+1, range_description, range_string, False], table_name=database.RANGES_TABLE_NAME, parametrs=[database.RANGES_ID, database.RANGES_DESCRIPTION, database.RANGES_RANGES, database.RANGES_IS_DEFAULT])

    # update default range
    change_default_range(ui_obj=ui_obj, range_description=range_description)

    # refresh table
    load_ranges_from_db_to_ui(ui_obj=ui_obj)


def change_default_range(ui_obj, range_description):
    # set all table cols default to false
    ui_obj.db.update_colomn_for_all_items(table_name=database.RANGES_TABLE_NAME, col_name=database.RANGES_IS_DEFAULT, value=False)

    # change selected algorithm to default
    ui_obj.db.update_column(table_name=database.RANGES_TABLE_NAME, searching_col_name=database.RANGES_DESCRIPTION, searching_value=range_description, col_name=database.RANGES_IS_DEFAULT, value=True)
    
    # refresh table
    load_ranges_from_db_to_ui(ui_obj=ui_obj)





def delete_range(ui_obj):
    # get selected report in ui table
    selected_id = -1
    for i in range(ui_obj.ranges_table.rowCount()):    
        if ui_obj.ranges_table.item(i, 0).checkState() == QtCore.Qt.Checked:
            selected_id = ui_obj.ranges_table.item(i, 1).text()
            break
    if selected_id == -1:
        return

    # delete record
    ui_obj.db.remove_record(col_name=database.RANGES_ID, id=selected_id, table_name=database.RANGES_TABLE_NAME)
    
    # refresh table
    load_ranges_from_db_to_ui(ui_obj=ui_obj)

        
#get ranges from db to ui
def add_selected_range_to_ui(ui_obj, change_default_range_=True):
    selected_id = -1
    for i in range(ui_obj.ranges_table.rowCount()):    
        if ui_obj.ranges_table.item(i, 0).checkState() == QtCore.Qt.Checked:
            selected_id = ui_obj.ranges_table.item(i, 1).text()
            selected_dis = ui_obj.ranges_table.item(i, 2).text()
            break
    if selected_id == -1:
        return

    # change default algo in database
    if change_default_range_:
        change_default_range(ui_obj=ui_obj, range_description=selected_dis)
    
    ui_obj.range_desc_lineedit.setText(selected_dis)

    res, ranges_list = ui_obj.db.retrive_all(table_name=database.RANGES_TABLE_NAME)
    if not res:
        return

    for i,dict in enumerate(ranges_list):
        if dict[database.RANGES_ID] == selected_id:
            selected_index = i

    temp_array = []
    ranges_dict = {}
    range_string = ranges_list[selected_index][database.RANGES_RANGES]

    temp_array = range_string.split(',')

    for itr, range_ in enumerate(temp_array):
        ranges_dict[itr] = [float(range_.split('-')[0]), float(range_.split('-')[1])]
    
    ###### update dictionary ins start
    ui_obj.algo_params.ranges_dict = ranges_dict
    print('range list: ', ui_obj.algo_params.ranges_dict)


    for i in range(ui_obj.algo_params.number_ranges):
        ##### removing all ranges
        ui_obj.algo_params.remove_category_range(True)
    
    for i in range(len(ranges_dict.keys())):
        ##### add new ranges to ui
        ui_obj.algo_params.add_category_range_from_db(ranges_dict[i][0], ranges_dict[i][1])


    ##### update range dictionary in algo-params class
    ui_obj.algo_params.ranges_dict = ranges_dict
    ui_obj.algo_params.ranges_colors = mcp.gen_color(cmap='jet', n=len(ui_obj.algo_params.ranges_dict.keys()))
    # print('ranges are set', ui_obj.algo_params.ranges_dict)
    reports.update_range_combobox_on_report_page(ui_obj)
    
    # ##### add selected range to labels in main window
    #### delete every obj in the layout
    deleteLayout(ui_obj.horizontalLayout_grading_percentages)
    for i, range_ in enumerate(ranges_dict.values()):
        item2= ''
        range_ = str(range_)
        range_ = range_.replace(',', '-')
        label_range = "ui_obj.range_label_in_main_detection_page_" + str(i)
        exec(label_range  + "=QLabel(str(range_))")
        exec(label_range + ".setAlignment(QtCore.Qt.AlignCenter)")
        label_percent = "ui_obj.percentage_label_in_main_detection_page_" + str(i)
        exec(label_percent  + "=QLabel(item2)")
        exec(label_percent + ".setAlignment(QtCore.Qt.AlignCenter)")
        exec("ui_obj.Vertical_Layout_" + str(i) + "=" + "QVBoxLayout()")
        exec("ui_obj.Vertical_Layout_" + str(i) + ".addWidget(" + label_range + ")")
        exec("ui_obj.Vertical_Layout_" + str(i) + ".addWidget(" + label_percent + ")")
        exec("ui_obj.horizontalLayout_grading_percentages.addLayout("+"ui_obj.Vertical_Layout_" + str(i)+")")

    ##### add selected circularity to labels in main window
    #### delete every obj in the layout
    deleteLayout(ui_obj.horizontalLayout_cicularity_percentages)
    circularity_range = ['[0 - 0.2]', '[0.2 - 0.4]', '[0.4 - 0.6]', '[0.6 - 0.8]', '[0.8 - 1.0]']
    for i, range_ in enumerate(circularity_range):
        item2= ''
        label_range = "ui_obj.cir_range_label_in_main_detection_page_" + str(i)
        exec(label_range  + "=QLabel(str(range_))")
        exec(label_range + ".setAlignment(QtCore.Qt.AlignCenter)")
        label_percent = "ui_obj.cir_percentage_label_in_main_detection_page_" + str(i)
        exec(label_percent  + "=QLabel(item2)")
        exec(label_percent + ".setAlignment(QtCore.Qt.AlignCenter)")
        exec("ui_obj.Vertical_Layout_" + str(i) + "=" + "QVBoxLayout()")
        exec("ui_obj.Vertical_Layout_" + str(i) + ".addWidget(" + label_range + ")")
        exec("ui_obj.Vertical_Layout_" + str(i) + ".addWidget(" + label_percent + ")")
        exec("ui_obj.horizontalLayout_cicularity_percentages.addLayout("+"ui_obj.Vertical_Layout_" + str(i)+")")
        
    



def deleteLayout(cur_lay):
    # QtGui.QLayout(cur_lay)
    
    if cur_lay is not None:
        while cur_lay.count():
            item = cur_lay.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
            else:
                deleteLayout(item.layout())
        # delete(cur_lay)


def update_percentages_on_main_window(ui_obj, grading_percentages, circularity_percentages):
    for i, range_percent in enumerate(grading_percentages):
        label_percent = "ui_obj.percentage_label_in_main_detection_page_" + str(i)
        exec(label_percent + '.setText(str(round(range_percent, 2)))')

    for i, cir_percent in enumerate(circularity_percentages):
        label_percent = "ui_obj.cir_percentage_label_in_main_detection_page_" + str(i)
        exec(label_percent + '.setText(str(round(cir_percent, 2)))')
        

def update_percentages_on_report_page(ui_obj, grading_range, grading_percentages, circularity_percentages):
    
    deleteLayout(ui_obj.horizontalLayout_grading_percentages_report)
    for i, range_percent in enumerate(grading_range):
        label_range = "ui_obj.range_label_in_report_page_" + str(i)
        exec(label_range  + "=QLabel(str(range_percent))")
        exec(label_range + ".setAlignment(QtCore.Qt.AlignCenter)")
        label_percent = "ui_obj.percentage_label_in_report_page_" + str(i)
        exec(label_percent  + "=QLabel()")
        exec(label_percent + ".setAlignment(QtCore.Qt.AlignCenter)")
        exec("ui_obj.Vertical_Layout_" + str(i) + "=" + "QVBoxLayout()")
        exec("ui_obj.Vertical_Layout_" + str(i) + ".addWidget(" + label_range + ")")
        exec("ui_obj.Vertical_Layout_" + str(i) + ".addWidget(" + label_percent + ")")
        exec("ui_obj.horizontalLayout_grading_percentages_report.addLayout("+"ui_obj.Vertical_Layout_" + str(i) + ")")

    for i, range_percent in enumerate(grading_percentages):
        label_percent = "ui_obj.percentage_label_in_report_page_" + str(i)
        exec(label_percent + '.setText(str(round(range_percent, 2)))')
    

    ##### add selected circularity to labels
    #### delete every obj in the layout
    deleteLayout(ui_obj.horizontalLayout_cicularity_percentages_report)
    circularity_range = ['[0 , 0.2]', '[0.2 , 0.4]', '[0.4 , 0.6]', '[0.6 , 0.8]', '[0.8 , 1.0]']
    for i, cir_percent in enumerate(circularity_percentages):
        
        label_range = "ui_obj.cir_range_label_in_report_page_" + str(i)
        exec(label_range  + "=QLabel(str(circularity_range[i]))")
        exec(label_range + ".setAlignment(QtCore.Qt.AlignCenter)")
        label_percent = "ui_obj.cir_percentage_label_in_report_page_" + str(i)
        exec(label_percent  + "=QLabel(str(round(cir_percent, 2)))")
        exec(label_percent + ".setAlignment(QtCore.Qt.AlignCenter)")
        exec("ui_obj.Vertical_Layout_" + str(i) + "=" + "QVBoxLayout()")
        exec("ui_obj.Vertical_Layout_" + str(i) + ".addWidget(" + label_range + ")")
        exec("ui_obj.Vertical_Layout_" + str(i) + ".addWidget(" + label_percent + ")")
        exec("ui_obj.horizontalLayout_cicularity_percentages_report.addLayout("+"ui_obj.Vertical_Layout_" + str(i)+")")

def add_selected_algo_params_to_ui(ui_obj, change_default_algo_=True):
    selected_des = ''
    for i in range(ui_obj.algo_param_table.rowCount()):    
        if ui_obj.algo_param_table.item(i, 0).checkState() == QtCore.Qt.Checked:
            selected_des = ui_obj.algo_param_table.item(i, 1).text()
            break

    if selected_des == '':
        return

    # change default algo in database
    if change_default_algo_:
        change_default_algo(ui_obj=ui_obj, record_description=selected_des)

    res, algo_param_list = ui_obj.db.retrive_all(table_name=database.ALGO_TABLE_NAME)
    if not res:
        return

    for i,dict in enumerate(algo_param_list):
        if dict[database.ALGO_DESCRIPTION] == selected_des:
            selected_index = i

    ui_obj.algo_desc_lineedit.setText(selected_des)

    ksize = int(algo_param_list[selected_index][database.ALGO_BLUR_KSIZE])
    ksize = ksize if ksize%2==1 else ksize
    ui_obj.blur_ksize_spin_2.setValue(ksize)
    ui_obj.algo_params.blur_ksize = ksize

    gray_thrs = int(algo_param_list[selected_index][database.ALGO_GRAY_THRS])
    ui_obj.gray_spin_2.setValue(gray_thrs)
    ui_obj.algo_params.gray_thrs = gray_thrs

    circ_acc = int(algo_param_list[selected_index][database.ALGO_MIN_CIRCULARITY])
    ui_obj.circ_acc_spin_2.setValue(circ_acc)
    circ_acc = circ_acc if circ_acc<=1 else circ_acc/100
    ui_obj.algo_params.circ_acc = circ_acc
