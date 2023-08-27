import sys
import cv2
from PyQt5 import QtWidgets, uic, QtCore, QtGui
from PyQt5.QtWidgets import *
from functools import partial
import pandas as pd
from backend import colors, texts, camera_connection, photoviewer, image_grabbing, detection, chart, camera_settings
from backend import database, reports, algo_settings, date, calender_ui

CAMER_WIDTH = 1920
CAMERA_HEIGHT = 1200

class Ui(QtWidgets.QMainWindow):
    """this class is used to build class for mainwindow to load GUI application

    :param QtWidgets: _description_
    """

    def __init__(self):
        """this function is used to laod ui file and build GUI application
        """

        super(Ui, self).__init__()
        
        # load ui file
        uic.loadUi('main_UI.ui', self)
        self.setWindowFlags(QtCore.Qt.WindowFlags(QtCore.Qt.FramelessWindowHint))
        
        #
        self.process_worker = None
        #___________________________________________________________________________
        #                             تابلوی ملک زاده
        #___________________________________________________________________________
        # app language  
        self.language = 'en'

        #
        self._old_pos = None
        self.debug = False

        #
        self.fps = 0
        
        # params ui
        # self.params_ui = params_ui.Params_Ui(ui_obj=self)

        # database object
        self.db = database.sqlite_database(name=database.DATABASE_NAME)
        self.db.connect()
        self.db.create_default_tables()
        

        # main detection object
        self.algo_params = detection.Algo_Params(ui_obj=self, params_ui_obj=self)
        self.detection_obj = detection.Grading(ui_obj=self, algo_parasm_obj=self.algo_params, debug=self.debug)

        ###### search in reports
        self.search_report_start_date = ''
        self.search_report_end_date = ''

        # button connector
        self.button_connector()

        # startup settings
        self.startup_settings()

        #### calibration page
        self.camera_connect_flag = False
        self.camera_obj = None
        self.images_list = []
        self.frame_itr = 0
        self.system_operating = False


        # self.image_frame.setMaximumWidth(300)
        # self.image_frame.setMinimumWidth(300)
        # self.label_main_frame.setMaximumWidth(300)
        # self.label_main_frame.setMinimumWidth(300) 
        


    def startup_settings(self):
        """this function is used to do startup settings on app start
        """
        #### disable page
        # self.disable_application(disable = True)

        # self.login_ui_obj = user_login.Login_User_Ui(ui_obj = self)
        # self.users_access_obj = users.Access_levels(ui_obj=self)

        self.algo_params.update_params()
        self.cam_settings = camera_settings.get_camera_params_from_ui(self)
        # photoviewer
        self.image_viewer = photoviewer.PhotoViewer()
        self.image_frame.layout().addWidget(self.image_viewer)
        self.set_image_on_photoviewer(image=None, set_raw=True)

        #### calibration window
        self.image_viewer_calibration = photoviewer.PhotoViewer()
        self.calibration_fram.layout().addWidget(self.image_viewer_calibration)
        self.set_image_on_label_calib(image=None, set_raw=True)
        camera_settings.get_camera_params_from_db_to_ui(db_obj=self.db, ui_obj=self)

        ##### show available cameras in comboBox of available camera in cam settings
        self.comboBox_SerialNumber.clear()
        available_cameras = camera_settings.get_available_cameras_list_serial_numbers()
        for i in range(len(available_cameras)):
            self.comboBox_SerialNumber.addItem(str(available_cameras[i]))

        # algorithms table
        algo_settings.load_algo_params_from_db_to_ui(ui_obj=self)
        algo_settings.load_ranges_from_db_to_ui(ui_obj=self)

        # chart
        chart.create_ranges_chart_on_ui(ui_obj=self)
        chart.create_circularity_chart_on_ui(ui_obj=self)

        # reports table
        reports.load_reports_from_db_to_ui(ui_obj=self)
        self.report_manager = reports.Report_Manager(ui_obj=self)


    def show_calender_start_date(self):

        ##### get all the years in database
        res, reports_list = self.db.retrive_all(table_name=database.REPORTS_TABLE_NAME)
        if not res:
            return
        years = []
        for report in reports_list:
            if report[database.REPORTS_DATE].split('/')[0] not in years:
                years.append(report[database.REPORTS_DATE].split('/')[0])

        ##### cal the calender ui object with the years
        cal = calender_ui.Calender(self, years, is_it_start=True)
        cal.show()
        self.search_report_start_date = cal.selected_date


    def show_calender_end_date(self):
        ##### get all the years in database
        res, reports_list = self.db.retrive_all(table_name=database.REPORTS_TABLE_NAME)
        if not res:
            return
        years = []
        for report in reports_list:
            if report[database.REPORTS_DATE].split('/')[0] not in years:
                years.append(report[database.REPORTS_DATE].split('/')[0])
        ##### cal the calender ui object with the years
        cal = calender_ui.Calender(self, years, is_it_start=False)
        cal.show()
        self.search_report_end_date = cal.selected_date
        

    def button_connector(self):
        """this function is used to connect ui buttons to their functions
        """
        #### calender in search in report
        self.report_search_start_date_btn.clicked.connect(partial(self.show_calender_start_date))
        self.report_search_end_date_btn.clicked.connect(partial(self.show_calender_end_date))

        #### search in report
        self.report_filter__clear_btn.clicked.connect(partial(lambda: reports.load_reports_from_db_to_ui(ui_obj=self, default_changed=True, filter_by_date_and_range=False, update_range_feilds=True, refresh_flag=True)))
        
        #### close , minimize, maximize
        self.close_btn.clicked.connect(partial(self.close_app))
        self.maximize_btn.clicked.connect(partial(self.maxmize_minimize))
        self.minimize_btn.clicked.connect(partial(self.minimize_win))

        #### login, register, user
        # self.user_login_btn.clicked.connect(partial(self.login_user))
        #
        self.camera_connect_btn_5.clicked.connect(partial(self.connect_camera))
        self.start_capturing_btn_5.clicked.connect(partial(self.main_detection))
        
        if self.stop_capturing_btn_5.clicked:
            self.stop_capturing_btn_5.clicked.connect(partial(lambda : detection.stop_message(ui_obj=self)))

        # params ui
        self.apply_btn_cam_setting.clicked.connect(partial(self.algo_params.update_camera_settings))      

        if self.reset_capturing_btn_5.clicked:
            self.reset_capturing_btn_5.clicked.connect(partial(lambda : self.detection_obj.message_reset_save(ui_obj=self)))
        
        self.camera_calib_btn.clicked.connect(partial(self.algo_params.connect_cammera_calib))
        self.calib_btn.clicked.connect(partial(self.algo_params.calibration))
        self.calib_debug_flag = self.checkBox_calib.isChecked()

        ###### algorithm setting page
        self.add_category_range.clicked.connect(partial(self.algo_params.add_category_range))
        self.remove_category_range.clicked.connect(partial(self.algo_params.remove_category_range))
        
        # Apply the granularity range
        if self.range_apply_pushButton.clicked:
            self.range_apply_pushButton.clicked.connect(partial(lambda: self.algo_params.apply_to_add_db()))

        # report table
        self.report_detail_btn.clicked.connect(partial(lambda: reports.report_show_details(ui_obj=self)))
        self.report_detail_return_btn.clicked.connect(partial(lambda: self.stackedWidget_rep.setCurrentWidget(self.reports_table_page)))
        self.excel_btn.clicked.connect(partial(lambda: reports.report_export_excel(ui_obj=self)))
        if self.delete_btn.clicked:
            self.delete_btn.clicked.connect(partial(lambda: reports.apply_to_delete_record(ui_obj=self)))
        self.refresh_btn.clicked.connect(partial(lambda: reports.load_reports_from_db_to_ui(ui_obj=self)))
        self.report_filter_by_name_btn.clicked.connect(partial(lambda: reports.load_reports_from_db_to_ui(ui_obj=self, default_changed=False, filter_by_date_and_range=False, update_range_feilds=False, refresh_flag=False)))
        self.report_range_combo.currentIndexChanged.connect(partial(lambda: reports.load_reports_from_db_to_ui(ui_obj=self, default_changed=True, filter_by_date_and_range=False, update_range_feilds=True, refresh_flag=False)))
        self.report_filter_btn.clicked.connect(partial(lambda: reports.load_reports_from_db_to_ui(ui_obj=self, default_changed=True, filter_by_date_and_range=True, update_range_feilds=False, refresh_flag=False)))
        #algorithm settings
        self.apply_btn_2.clicked.connect(partial(lambda: algo_settings.set_algo_params_from_ui_to_db(ui_obj=self)))
        self.algo_del_btn.clicked.connect(partial(lambda: algo_settings.delete_algo(ui_obj=self)))
        
        if self.del_btn_range.clicked:
            self.del_btn_range.clicked.connect(partial(lambda: algo_settings.apply_to_delete_range(ui_obj=self)))

        ##### range of grading setting 
        self.apply_btn_range.clicked.connect(partial(lambda: algo_settings.add_selected_range_to_ui(ui_obj=self)))


        ##### algorithm setting apply
        self.param_apply_btn.clicked.connect(partial(lambda: algo_settings.add_selected_algo_params_to_ui(ui_obj=self)))


    def close_app(self):
        """
        this function closes the app
        Inputs: None
        Returns: None
        """

        # close app window and exit the program
        if self.system_operating:
            self.show_alert_window('Exit Confirm', 'Detection Still Running', need_confirm=False)
        else:
            if self.camera_connect_flag:
                self.show_alert_window('Exit Confirm', 'Camera Still Connected', need_confirm=False)
            else:
                res = self.show_alert_window('Exit Confirm', 'Are You Sure You Want to Close the Program?', need_confirm=True)
                if res:
                    self.close()
                    sys.exit()
                else:
                    return
    

    def maxmize_minimize(self):
        """
        this function chages the window size of app
        Inputs: None
        Returns: None
        """

        if self.isMaximized():
            self.showNormal()
            self.maximize_btn.setToolTip(texts.TITLES['maximize'][self.language])  

        else:
            self.showMaximized()
            self.groupBox_2
            self.maximize_btn.setToolTip(texts.TITLES['restore_down'][self.language])  
    

    def minimize_win(self):
        """
        this function minimizes the app to taskbar
        Inputs: None
        Returns: None
        """
        
        self.showMinimized()
    

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
    

    def table_item_checked(self, item):
        table = self.sender()
        table_obj = eval('self.%s' % (table.objectName()))

        row = table_obj.indexFromItem(item).row()
        table_obj.itemChanged.disconnect(self.table_item_checked)

        # remove other checked rows
        for i in range(table_obj.rowCount()):    
            if i!=row and table_obj.item(i, 0).checkState() == QtCore.Qt.Checked:

                table_obj.item(i, 0).setCheckState(QtCore.Qt.Unchecked)
        
        table_obj.itemChanged.connect(self.table_item_checked)
    

    def show_alert_window(self, title, message, need_confirm=False):
        """this function is used to create a confirm window
        :param title: _description_, defaults to 'Message'
        :type title: str, optional
        :param message: _description_, defaults to 'Message'
        :type message: str, optional
        :return: _description_
        :rtype: _type_
        """

        # create message box
        alert_window = QtWidgets.QMessageBox()
        # icon
        alert_window.setIcon(QtWidgets.QMessageBox.Warning)
        # message and title
        alert_window.setText(message)
        alert_window.setWindowTitle(title)
        # buttons
        if not need_confirm:
            alert_window.setStandardButtons(QtWidgets.QMessageBox.Ok)
            alert_window.button(QtWidgets.QMessageBox.Ok).setText(texts.TITLES['ok'][self.language])
        else:
            alert_window.setStandardButtons(QtWidgets.QMessageBox.Cancel | QtWidgets.QMessageBox.Ok)
            alert_window.button(QtWidgets.QMessageBox.Ok).setText(texts.TITLES['confirm'][self.language])
            alert_window.button(QtWidgets.QMessageBox.Cancel).setText(texts.TITLES['cancel'][self.language])

        # show
        returnValue = alert_window.exec()

        if not need_confirm:
            return True if returnValue == QtWidgets.QMessageBox.Ok else True
        else:
            return True if returnValue == QtWidgets.QMessageBox.Ok else False
    

    def set_image_on_photoviewer(self, image, set_raw=False):
        """this function is used to set an image to a label

        :param label_obj: _description_
        :param image: _description_
        """
            
        # load raw image to set on  on label
        self.image=image
        try:
            if set_raw:
                image = cv2.imread('Icons/no_image.png')       
        except:
            # return
            pass
        
        # convert to rgb if needed
        if len(image.shape)<3:
            image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
    
        height, width, channels = image.shape
        bytesPerLine = channels * width

        # convert cv2 image to pyyqt image
        qImg = QtGui.QImage(image.data, width, height, bytesPerLine, QtGui.QImage.Format_RGB888)
        pixmap = QtGui.QPixmap.fromImage(qImg)
        pixmap_image = QtGui.QPixmap(pixmap)
        
        # set image on image viewer
        self.image_viewer.setPhoto(pixmap=pixmap_image)
        

        
    
    def set_image_on_label_calib(self, image, set_raw=False):
        """this function is used to set an image to a label

        :param label_obj: _description_
        :param image: _description_
        """
            
        # load raw image to set on  on label
        try:
            if set_raw:
                image = cv2.imread('Icons/no_image.png')
        except:
            pass
        
        # convert to rgb if needed
        if len(image.shape)<3:
            image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
    
        height, width, channels = image.shape
        bytesPerLine = channels * width

        # convert cv2 image to pyyqt image
        qImg = QtGui.QImage(image.data, width, height, bytesPerLine, QtGui.QImage.Format_RGB888)
        pixmap = QtGui.QPixmap.fromImage(qImg)
        pixmap_image = QtGui.QPixmap(pixmap)

        # set image on image viewer
        self.image_viewer_calibration.setPhoto(pixmap=pixmap_image)



    def set_text_on_label(self, label_name, text=''):
        # convert label name to pyqt object if is string
        label = eval('self.%s' % (label_name)) if isinstance(label_name, str) else label_name

        label.setText(text)
    

    def show_message(self, label_name=None, text='', level=0, clearable=True):
        """this function is used to show input message in message label, also there is a message level determining the color of label, and a timer to clear meesage after a while

        :param text: _description_, defaults to ''
        :param level: _description_, defaults to 0
        :param clearable: _description_, defaults to True
        """

        level = 1 if level<0 or level>2 else level

        # convert label name to pyqt object if is string
        label_name = self.msg_label if label_name is None else label_name
        label = eval('self.%s' % (label_name)) if isinstance(label_name, str) else label_name

        try:
            # set message
            if text != '':
                if level == 0:
                    label.setText(text)
                    label.setStyleSheet('padding-left: 10px; padding-right: 10px; background: %s; color:white;' % (colors.SUCCESS_GREEN))
                #
                if level == 1:
                    label.setText(text)
                    label.setStyleSheet('padding-left: 10px; padding-right: 10px; background: %s; color:white;' % (colors.WARNING_YELLOW))
                #
                if level == 2:
                    label.setText(text)
                    label.setStyleSheet('padding-left: 10px; padding-right: 10px; background: %s; color:white;' % (colors.FAILED_RED))

                # timer to clear the message
                if clearable:
                    QtCore.QTimer.singleShot(5000, lambda: self.show_message(label_name=label_name))

            # clear the message after timeout
            else:
                label.setText('')
                label.setStyleSheet('')
        
        except Exception as e:
            return
    

    def update_grading_chart(self, grading_params, circ_acc):
        chart.update_chart(ui_obj=self, grading_params=grading_params, circ_acc=circ_acc)
        algo_settings.update_percentages_on_main_window(self, grading_percentages=grading_params, circularity_percentages=circ_acc)


    def connect_camera(self):
        """this function is used to connect/disconnect camera
        """

        self.cam_settings = camera_settings.get_camera_params_from_ui(self)

        # not connected to camers, try to connect
        if not self.camera_connect_flag:
            try:
                # get available cameras serials
                collector = camera_connection.Collector(serial_number='', list_devices_mode=True)
                serial_list = collector.serialnumber()
                del collector

                if len(serial_list) == 0:
                    self.show_message(label_name=None, text=texts.WARNINGS['some_cameras_not_connected'][self.language], level=1, clearable=True)
                    return
                
                ##### CAMERA SETTINGS
                if self.cam_settings[database.CAMERA_TRIGGER_MODE] == '0':
                    triggerMode = False
                elif self.cam_settings[database.CAMERA_TRIGGER_MODE] == '1':
                    triggerMode = True
                
               
                self.collector = camera_connection.Collector(serial_number=self.cam_settings[database.CAMERA_SERIAL], 
                                    gain=self.cam_settings[database.CAMERA_GAIN], exposure=self.cam_settings[database.CAMERA_EXPOSURE],
                                     max_buffer=20, trigger=triggerMode, delay_packet=50, packet_size=1500,
                                      frame_transmission_delay=0, width=CAMER_WIDTH, height=CAMERA_HEIGHT, offet_x=0, offset_y=0,
                                       manual=True, list_devices_mode=False, trigger_source='Software')
                res, _ = self.collector.start_grabbing()

                if not res:
                    self.show_message(label_name=None, text=texts.ERRORS['camera_connect_failed'][self.language], level=2, clearable=True)
                    return
               
                # camera connected, update ui fileds
                self.show_message(label_name=None, text=texts.MESSEGES['camera_connect'][self.language], level=0, clearable=True)
                self.camera_connect_flag = True
                self.camera_connect_btn_5.setStyleSheet('''QPushButton{background-color:
                                                    qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 rgba(12, 80, 139, 255),
                                                    stop:0.863636 rgba(12, 80, 139, 255), stop:0.885 rgba(0, 255, 0, 255),
                                                    stop:1 rgba(0, 255, 0, 255));}''')
                #
                
                self.update_ui_labels(label=self.camera_connect_label, state=True)

                self.start_capturing_btn_5.setEnabled(True)
                self.stop_capturing_btn_5.setEnabled(False)

           
            except Exception as e:
                print(e)
                self.show_message(label_name=None, text=texts.ERRORS['camera_connect_failed'][self.language], level=2, clearable=True)
                
        # connected to cameras, try to dissconnect
        else:            
            self.stop_detect()

            # dissconnect camera
            self.collector.stop_grabbing()
            self.collector = None

            # camera connected, update ui fileds
            self.show_message(label_name=None, text=texts.WARNINGS['camera_disconnect'][self.language], level=1, clearable=True)
            self.camera_connect_flag = False
            #
            self.camera_connect_btn_5.setStyleSheet('''QPushButton{background-color:
                qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 rgba(12, 80, 139, 255),
                stop:0.863636 rgba(12, 80, 139, 255), stop:0.885 rgba(255, 0, 0, 255),
                stop:1 rgba(255, 0, 0, 255));}''')
                    
            self.start_capturing_btn_5.setEnabled(False)
            self.update_ui_labels(label=self.camera_connect_label, state=False)
            self.stop_capturing_btn_5.setEnabled(False)

            #### connect from setting page
            self.Config_2.setEnabled(True)
            self.report_tab.setEnabled(True)
            #     # save to database
            # if len(self.contours_dict.keys())>0:
            #     detection_id = self.ui_obj.record_name_text.text()
            #     if detection_id != '':
            #         # check report id to be unique
            #         res, reports_list = self.ui_obj.db.retrive_all(table_name=database.REPORTS_TABLE_NAME)
            #         for rep in reports_list:
            #             if rep[database.REPORTS_ID] == detection_id:
            #                 detection_id += '_2'
            #                 break

            #         self.ui_obj.db.add_record(data=[detection_id, self.start_date, self.start_time, str(list(self.algo_parasm_obj.ranges_dict.keys())), "./database/"+detection_id], table_name=database.REPORTS_TABLE_NAME,
            #                                 parametrs=[database.REPORTS_ID, database.REPORTS_DATE, database.REPORTS_TIME, database.REPORTS_GRADING_RANGES, database.REPORTS_SAVE_PATH])
            #         reports.save_report(report_id=detection_id, contours_dict=self.contours_dict, px_values=self.algo_parasm_obj.Calibration_Coefficients, circ_acc_thrs=self.algo_parasm_obj.circ_acc, ranges_dict=self.algo_parasm_obj.ranges_dict)
            # if not self.ui_obj.record_name_text.text():
            #     self.ui_obj.record_name_text.setText(date.get_datetime())
        



    def stop_detect(self):
        # self.start_capturing_btn.setEnabled(False)
        if self.process_worker != None:
            self.process_worker.stop = True
            self.camera_worker.stop = True
        # self.stop_capturing_btn.setEnabled(True)
        self.start_capturing_btn_5.setEnabled(True)
        self.camera_connect_btn_5.setEnabled(True)
        self.stop_capturing_btn_5.setEnabled(False)
        self.update_ui_labels(label=self.camera_capture_label, state=False)
        cv2.waitKey(500)
        self.set_image_on_photoviewer(image=None, set_raw=True)
        #### connect from setting page
        self.Config_2.setEnabled(True)
        self.report_tab.setEnabled(True)
        # # save to database
        # if len(self.detection contours_dict.keys())>0:
        #     detection_id = self.ui_obj.record_name_text.text()
        #     if detection_id != '':
        #         # check report id to be unique
        #         res, reports_list = self.ui_obj.db.retrive_all(table_name=database.REPORTS_TABLE_NAME)
        #         for rep in reports_list:
        #             if rep[database.REPORTS_ID] == detection_id:
        #                 detection_id += '_2'
        #                 break

        #         self.ui_obj.db.add_record(data=[detection_id, self.start_date, self.start_time, str(list(self.algo_parasm_obj.ranges_dict.keys())), "./database/"+detection_id], table_name=database.REPORTS_TABLE_NAME,
        #                                 parametrs=[database.REPORTS_ID, database.REPORTS_DATE, database.REPORTS_TIME, database.REPORTS_GRADING_RANGES, database.REPORTS_SAVE_PATH])
        #         reports.save_report(report_id=detection_id, contours_dict=self.contours_dict, px_values=self.algo_parasm_obj.Calibration_Coefficients, circ_acc_thrs=self.algo_parasm_obj.circ_acc, ranges_dict=self.algo_parasm_obj.ranges_dict)
        # if not self.ui_obj.record_name_text.text():
        #     self.ui_obj.record_name_text.setText(date.get_datetime())




    # update UI flag indicator labels
    def update_ui_labels(self, label, state=False):
        if state:
            label.setStyleSheet('background-color: green;')
        else:
            label.setStyleSheet('background-color: red;')



    def main_detection(self):
        """
        this function is used to start/stop frame grabbing
        """
        if not self.system_operating:
            self.show_message(label_name=None, text=texts.WARNINGS['detection_activation'][self.language], level=0, clearable=True)
            
            #### disconnect from setting page
            self.Config_2.setEnabled(False)
            self.report_tab.setEnabled(False)
            

            # assign new default values to
            if not self.record_name_text.text():
                self.record_name_text.setText(date.get_datetime())

            # Create frame grabbing worker
            self.camera_worker = image_grabbing.Camera_Image_Grabber_Worker()
            self.camera_worker.assign_parameters(ui_obj=self, camera_obj=self.collector)
            # Create QThread object
            self.camera_thread = QtCore.QThread()
            # assign worker to the thread
            self.camera_worker.moveToThread(self.camera_thread)
            # Connect signals and slots
            self.camera_thread.started.connect(partial(self.camera_worker.grab_frame))
            self.camera_worker.finished.connect(partial(self.camera_thread.quit))
            self.camera_thread.finished.connect(partial(self.camera_thread.deleteLater))
            self.camera_thread.start()

            # Create image processing worker
            self.process_worker = image_grabbing.Image_Process_Worker()
            self.process_worker.assign_parameters(ui_obj=self)
            # Create QThread object
            self.process_thread = QtCore.QThread()
            # assign worker to the thread
            self.process_worker.moveToThread(self.process_thread)
            # Connect signals and slots
            self.process_thread.started.connect(partial(self.process_worker.process_frames))
            self.process_worker.finished.connect(partial(self.process_thread.quit))
            self.process_worker.show_image.connect(partial(self.set_image_on_photoviewer))
            self.process_worker.show_image.connect(partial(self.set_image_on_label_calib))
            self.process_worker.update_chart.connect(partial(self.update_grading_chart))
            # self.process_worker.update_n_detected.connect(partial(self.set_text_on_label))
            
            self.process_thread.finished.connect(partial(self.process_thread.deleteLater))
            self.process_thread.start()

            self.start_capturing_btn_5.setEnabled(False)
            # self.camera_connect_btn_5.setEnabled(False)
            self.stop_capturing_btn_5.setEnabled(True)
            self.update_ui_labels(label=self.camera_capture_label, state=True)
            self.update_ui_labels(label=self.calibration_label, state=True)

    def show_mesagges_setting(self, label_name, text, color='green'):
        name=label_name
        if text != None:
            label_name.setText(text)
            label_name.setStyleSheet("color:{}".format(color))       
            # threading.Timer(20000, self.show_mesagges, args=(name,None)).start()
        else:
            label_name.setText('')  


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = Ui()
    window.show()
    app.exec_()
