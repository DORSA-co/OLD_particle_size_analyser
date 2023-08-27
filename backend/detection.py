import numpy as np
import cv2
import json
import datetime
from mycolorpy import colorlist as mcp
from PIL import ImageColor
import pandas as pd
from PyQt5 import QtWidgets, uic, QtCore, QtGui
from PyQt5.QtGui import * 
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import calibrate
from backend import date, texts, chart, camera_connection, image_grabbing, photoviewer, camera_settings, logger, reports
from functools import partial
import openpyxl
from backend import calibration_class, database, reports, algo_settings
import datetime
import math
import time



def draw_contours_on_image(image, cnts):
    """this function is used to draw contours of the founded edges

    :param image: _description_
    :param cnts: _description_
    :return: _description_
    """
    if len(image.shape)<3:
        image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
    image = cv2.drawContours(image, cnts , -1, (0,255,0), thickness=1)
    return image



class Algo_Params():
    """this class is used to get/manage grading algorithm params from ui

    :return: _description_
    """

    def __init__(self, ui_obj, params_ui_obj):
        self.ui_obj = ui_obj
        self.params_ui_obj = params_ui_obj
        self.ranges_dict = {}
        self.ranges_colors = []
        self.blur_ksize = None
        self.gray_thrs = None
        self.circ_acc = None
        self.Calibration_Coefficients = [0, 0, 0]
        self.number_ranges = 0
        # self.frame_to_calibrate = None
        ##### camera connection for calibration
        self.camera_connect_flag = False
        self.camera_obj = None
        self.images_list = []
        self.frame_itr = 0

        self.obj_calibration_class = calibration_class.calibration_class(self.ui_obj)
        
        # self.stop_capturing_btn_5.clicked.connect(self.)

    def update_camera_settings(self):
        # update camera params on dataabse
        logger.logger('Camera Setting')
        camera_settings.set_camera_params_from_ui_to_db(ui_obj=self.ui_obj)

        logger.logger('Camera Setting: update cam settings')
        #### main camera and calibration camera are disconnected
        if not self.obj_calibration_class.camera_connect_flag and not self.ui_obj.camera_connect_flag:
            logger.logger('Camera Setting: neither camera connected')
            #### get params from ui in a dictionary format
            self.obj_calibration_class.camera_params = camera_settings.get_camera_params_from_ui(self.ui_obj)
            self.ui_obj.cam_settings = camera_settings.get_camera_params_from_ui(self.ui_obj)
            self.obj_calibration_class.connect_func()

        #### camera in main window connected
        elif self.ui_obj.camera_connect_flag:
            logger.logger('Camera Setting: main camera connected')
            #### disconnect camera in main menu
            self.ui_obj.connect_camera()
            #### set new params
            self.obj_calibration_class.camera_params = camera_settings.get_camera_params_from_ui(self.ui_obj)
            self.ui_obj.cam_settings = camera_settings.get_camera_params_from_ui(self.ui_obj)
            self.obj_calibration_class.connect_func()


        #### camera connected in calibration window
        elif self.obj_calibration_class.camera_connect_flag:
            logger.logger("Camera Setting: camera connected in calibration page")
            #### disconnect camera in calibration window
            self.obj_calibration_class.connect_func()
            #### set new params
            self.obj_calibration_class.camera_params = camera_settings.get_camera_params_from_ui(self.ui_obj)
            self.ui_obj.cam_settings = camera_settings.get_camera_params_from_ui(self.ui_obj)
            self.obj_calibration_class.connect_func()



    def update_params(self):
        
        self.ranges_dict.clear()
        algo_settings.add_selected_range_to_ui(self.ui_obj)
        self.apply_category_range()
        self.ranges_colors = mcp.gen_color(cmap='jet', n=len(self.ranges_dict.keys()))
        # other parameters
        self.blur_ksize = int(self.ui_obj.blur_ksize_spin_2.value())
        self.blur_ksize = self.blur_ksize if self.blur_ksize%2==1 else self.blur_ksize+1
        self.gray_thrs = self.ui_obj.gray_spin_2.value()
        self.circ_acc = self.ui_obj.circ_acc_spin_2.value()
        self.circ_acc = self.circ_acc if self.circ_acc<=1 else self.circ_acc/100
        
        ###### read pre-calculated value from file
        try:
            df1 = pd.read_csv('params.csv', index_col=0)
            d = df1.values
            
            self.Calibration_Coefficients = [float(d[0, 0]), float(d[1, 0]), float(d[2, 0])]
            logger.logger("read calibration file successfully: " + str(self.Calibration_Coefficients))
            self.ui_obj.update_ui_labels(label=self.ui_obj.calibration_label, state=True)
            self.ui_obj.show_message(self.ui_obj.label_calibA, str(d[0, 0]), clearable = False)
            self.ui_obj.show_message(self.ui_obj.label_calibB, str(d[1, 0]), clearable = False)
            self.ui_obj.show_message(self.ui_obj.label_pxvalue, str(d[2, 0]), clearable = False)
             # update chart
            chart.create_ranges_chart_on_ui(ui_obj=self.ui_obj)
            chart.create_circularity_chart_on_ui(ui_obj=self.ui_obj)
        except Exception as e:
            print("parameter reading error", e)
            self.ui_obj.show_alert_window(title=texts.TITLES['error'][self.ui_obj.language], message=texts.WARNINGS['calibration_file_does_not_exist'][self.ui_obj.language], need_confirm=False)

            # update chart
            chart.create_ranges_chart_on_ui(ui_obj=self.ui_obj)
            chart.create_circularity_chart_on_ui(ui_obj=self.ui_obj)
    
    
    def add_category_range(self):
        #### adding a row in ranges
        i = self.number_ranges
        if i > 10: ##### limit of only 10 ranges
            self.ui_obj.show_message(self.ui_obj.label_msg_range, "You have reached the range limit",level=1, clearable = True)
            return

        ##### adding two spinboxes in setting of ranges
        spinbox_low_name = "self.ui_obj.SpinBox_low_" + str(i)
        exec(spinbox_low_name  + "=QDoubleSpinBox(self.ui_obj)")
        spinbox_high_name = "self.ui_obj.SpinBox_high_" + str(i)
        exec(spinbox_high_name  + "=QDoubleSpinBox(self.ui_obj)")
 
        exec("self.ui_obj.Horizontal_Layout_" + str(i) + "=" + "QHBoxLayout()")
        exec("self.ui_obj.verticalLayout_13.addLayout("+"self.ui_obj.Horizontal_Layout_" + str(i)+")")
        exec("self.ui_obj.Horizontal_Layout_" + str(i)+".addWidget("+spinbox_low_name+ ")")
        exec("self.ui_obj.Horizontal_Layout_" + str(i)+".addWidget("+spinbox_high_name+ ")")
        self.number_ranges += 1
        

    def add_category_range_from_db(self, low, high):
        ###### adding one range from db to ui
        i = self.number_ranges
        spinbox_low_name = "self.ui_obj.SpinBox_low_" + str(i)
        exec(spinbox_low_name  + "=QDoubleSpinBox(self.ui_obj)")
        spinbox_high_name = "self.ui_obj.SpinBox_high_" + str(i)
        exec(spinbox_high_name  + "=QDoubleSpinBox(self.ui_obj)")
 
        exec("self.ui_obj.Horizontal_Layout_" + str(i) + "=" + "QHBoxLayout()")
        exec("self.ui_obj.verticalLayout_13.addLayout("+"self.ui_obj.Horizontal_Layout_" + str(i)+")")
        exec("self.ui_obj.Horizontal_Layout_" + str(i)+".addWidget("+spinbox_low_name+ ")")
        exec("self.ui_obj.Horizontal_Layout_" + str(i)+".addWidget("+spinbox_high_name+ ")")
        
        exec(spinbox_low_name + ".setValue("+ str(low) +")")
        exec(spinbox_high_name + ".setValue("+ str(high) +")")

        self.number_ranges += 1

    def remove_category_range(self, load_from_db_flag = False):
        
        if not load_from_db_flag:
            #### make sure there are two rows left
            if self.number_ranges > 2:
                #### remove last item from dictionary
                try:
                    del self.ranges_dict[self.number_ranges-1]
                except:
                    pass

                #### reduce number of ranges by 1
                self.number_ranges -= 1
                
                #### remove spinboxes from ui
                spinbox_low_name = "self.ui_obj.SpinBox_low_" + str(self.number_ranges)
                exec(spinbox_low_name + ".deleteLater()")
                spinbox_high_name = "self.ui_obj.SpinBox_high_" + str(self.number_ranges)
                exec(spinbox_high_name   + ".deleteLater()")
            
            else:
                self.ui_obj.show_message(self.ui_obj.label_msg_range, "You have reached the range limit",level=1, clearable = True)

        else:
            ##### removing all categories not leaving any
            #### remove last item from dictionary
            try:
                del self.ranges_dict[self.number_ranges-1]
            except:
                pass

            #### reduce number of ranges by 1
            self.number_ranges -= 1
            
            #### remove spinboxes from ui
            spinbox_low_name = "self.ui_obj.SpinBox_low_" + str(self.number_ranges)
            exec(spinbox_low_name + ".deleteLater()")
            spinbox_high_name = "self.ui_obj.SpinBox_high_" + str(self.number_ranges)
            exec(spinbox_high_name   + ".deleteLater()")
            self.ranges_colors = mcp.gen_color(cmap='jet', n=len(self.ranges_dict.keys()))


    def apply_category_range(self, add_to_db=False):

        for i in range(self.number_ranges):

            spinbox_low_name = "self.ui_obj.SpinBox_low_" + str(i)
            spinbox_high_name = "self.ui_obj.SpinBox_high_" + str(i)

            #### add range to dictionary
            exec("self.ranges_dict["+str(i)+"] = [float("+spinbox_low_name+".value()), float("+spinbox_high_name+".value())]")
            
            #### low part of range must be lower than higher part!!! 
            if self.ranges_dict[i][0] > self.ranges_dict[i][1]:
                self.ui_obj.show_message(self.ui_obj.label_msg_range, "error in row: "+str(i+1),level=1, clearable = True)
                if i > 0:

                    ##### higher part and lower part of next part must be same
                    if self.ranges_dict[i][0] != self.ranges_dict[i-1][1]:

                        self.ui_obj.show_message(self.ui_obj.label_msg_range, "missing some part of range in line: "+str(i+1),level=1, clearable = True)
            
            self.ranges_colors = mcp.gen_color(cmap='jet', n=len(self.ranges_dict.keys()))
        reports.update_range_combobox_on_report_page(self.ui_obj)
        
        # add to database
        if add_to_db:
            algo_settings.add_range_to_db(ui_obj=self.ui_obj, ranges_dict=self.ranges_dict)
        reports.update_range_combobox_on_report_page(self.ui_obj)


    def apply_to_add_db(self):
        button_answer = self.ui_obj.show_alert_window(title=texts.TITLES['error'][self.ui_obj.language], message=texts.WARNINGS['are_you_sure'][self.ui_obj.language], need_confirm=True)
        if button_answer == True:
            self.apply_category_range(add_to_db=True)       
    
  
    ###### calibration function
    def calibration(self):
        '''
        calling calibration function with 6 rectangles and the rest...
        ''' 
        if self.obj_calibration_class.camera_connect_flag:
            # stop frame grabbing thread
            self.obj_calibration_class.camera_worker.stop = True
            frame = self.obj_calibration_class.frame_to_detect
            
            min_area = self.ui_obj.small_area_box.value()
            max_area = self.ui_obj.large_area_box.value()
            gray_thrs = self.ui_obj.threshold_calib_box.value()
            success_flag, self.Calibration_Coefficients = calibrate.apply_pxvalue_calibration(frame,
                             True, self.ui_obj.checkBox_calib.isChecked(),
                              min_area, max_area, gray_thrs)
            if success_flag:    
                df = pd.DataFrame(data=self.Calibration_Coefficients)
                df.to_csv('params.csv', header=['params'])
                self.ui_obj.show_message(self.ui_obj.label_calibA, str(self.Calibration_Coefficients[0]), clearable = False)
                self.ui_obj.show_message(self.ui_obj.label_calibB, str(self.Calibration_Coefficients[1]), clearable = False)
                self.ui_obj.show_message(self.ui_obj.label_pxvalue, str(self.Calibration_Coefficients[2]), clearable = False)
            else:
                self.ui_obj.show_alert_window(title=texts.TITLES['error'][self.ui_obj.language], message=texts.WARNINGS['was_not_able_to_calibrate'][self.ui_obj.language], need_confirm=False)
        
        else:
            self.ui_obj.show_message(self.ui_obj.msg_label_2, "camera not connected", clearable = True)


    def connect_cammera_calib(self):
        self.obj_calibration_class.camera_params = camera_settings.get_camera_params_from_ui(self.ui_obj)
        self.obj_calibration_class.connect_func()
def stop_message (ui_obj):
    button_answer = ui_obj.show_alert_window(title=texts.TITLES['error'][ui_obj.language], message=texts.WARNINGS['are_you_sure_stop'][ui_obj.language], need_confirm=True)
    if button_answer == True:
        ui_obj.stop_detect()

class Grading():
    """this class is used to grading
    """

    def __init__(self, ui_obj, algo_parasm_obj, debug=True, debug_scale=0.4):
        # hyper params
        self.ui_obj = ui_obj
        self.debug = debug
        self.debug_scale = debug_scale
        self.algo_parasm_obj = algo_parasm_obj
        #
        self.grading_ranges_arr = None
        self.n_objects = 0
        self.circle_acc = [0]
        #
        self.contours_dict = {}
        self.image_itr = 0
        ############ update algorithm parameters
        #
        self.wait_to_save_last_results_flag = False
        algo_parasm_obj.update_params()
    
    
    def message_reset_save(self, ui_obj):
        button_answer = ui_obj.show_alert_window(title=texts.TITLES['error'][ui_obj.language], message=texts.WARNINGS['are_you_sure_save_reset'][ui_obj.language], need_confirm=True)
        if button_answer == True:
            self.start_new_detection()
        else:
            print("cancle")

    def start_new_detection(self):
        """this function is used to start new detection session
        """
        
        # save last result to database
        self.wait_to_save_last_results_flag = True
        if len(self.contours_dict.keys())>0:
            # if self.ui_obj.record_name_text.text() == '':
            detection_id = date.get_datetime()                
            # else:
            #     detection_id = self.ui_obj.record_name_text.text()

            if detection_id != '':
                # check report id to be unique
                res, reports_list = self.ui_obj.db.retrive_all(table_name=database.REPORTS_TABLE_NAME)
                for rep in reports_list:
                    if rep[database.REPORTS_ID] == detection_id:
                        detection_id += '_2'
                        break

                self.ui_obj.db.add_record(data=[detection_id, self.start_date, self.start_time, self.grading_range_description(),str(list((self.grading_ranges_arr / self.grading_ranges_arr.sum()) * 100)),"./database/"+detection_id],
                                         table_name=database.REPORTS_TABLE_NAME,
                                        parametrs=[database.REPORTS_ID, database.REPORTS_DATE, database.REPORTS_TIME, database.REPORTS_GRADING_RANGES_DESCRIPTION, database.REPORTS_PERCENTAGES, database.REPORTS_SAVE_PATH])
                
                reports.save_report(report_id=detection_id, contours_dict=self.contours_dict, px_values=self.algo_parasm_obj.Calibration_Coefficients, circ_acc_thrs=self.algo_parasm_obj.circ_acc, ranges_dict=self.algo_parasm_obj.ranges_dict)
        
        if not self.ui_obj.record_name_text.text():
            self.ui_obj.record_name_text.setText(date.get_datetime())
        self.start_time = date.get_time()
        self.start_date = date.get_date()
        self.grading_ranges_arr = np.zeros((len(self.algo_parasm_obj.ranges_dict.keys())))
        self.n_objects = 0
        self.circle_acc = [0]
        self.circ_acc_array = np.array([0]*5)
        #
        self.contours_dict = {}
        self.image_itr = 0

        self.ui_obj.images_list.clear()
        # time.sleep(1)
        # cv2.waitKey(2000)
        chart.create_ranges_chart_on_ui(ui_obj=self.ui_obj)
        chart.create_circularity_chart_on_ui(ui_obj=self.ui_obj)
        # chart.reset_chart(ui_obj=self.ui_obj)
        self.wait_to_save_last_results_flag = False
        logger.logger('reset')
    

    def end_detection(self):
        """this function is used to end a detection session and return results
        """
        self.end_time = date.get_time()
    
    def volume_of_cuntour(self, w, h):
        vol = (4/3) * np.pi * (w*w*w)
        # w_mm = (w_px * self.algo_parasm_obj.px_value)*(0.904)/2
        # h_mm = (h_px * self.algo_parasm_obj.px_value)*(0.904)/2

        # print("w, h: ", w_mm, h_mm)

        # mean_volumes = (volume1+volume2)/2
        # # max_volumes = max(volume1,volume2)
        # print("volume_of_cuntour : ",vol)
        return vol
    
    def grading_range_description(self):
        res, ranges_list = self.ui_obj.db.retrive_all(table_name=database.RANGES_TABLE_NAME)
        # print(res)
        if not res:
            return
        else:
            for item in ranges_list:
                # print(item)
                if item[database.RANGES_IS_DEFAULT] == 'True':
                    return item[database.RANGES_DESCRIPTION]
                else:
                    # return
                    print('didnt find description')


    def detect(self, image): 
        # rgb to gray
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape)>2 else image
        if self.debug:
            cv2.imshow('Gray Image', cv2.resize(gray, None, fx=self.debug_scale, fy=self.debug_scale))
            cv2.waitKey(0)

        # bulr image
        gray = cv2.blur(gray,(3,3)) 
        gray = cv2.blur(gray,(7,7))
        gray = cv2.blur(gray,(3,3))
        # kernel = self.algo_parasm_obj.blur_ksize
        # gray = cv2.blur(gray, (kernel, kernel))
        if self.debug:
            cv2.imshow('Image Bluring', cv2.resize(gray, None, fx=self.debug_scale, fy=self.debug_scale))
            cv2.waitKey(0)
        kernel = np.ones((3,3),np.uint8)
        gray = cv2.erode(gray,kernel,iterations=2)
        # gray threshold

        _, objects_mask = cv2.threshold(gray, self.algo_parasm_obj.gray_thrs, 255, cv2.THRESH_BINARY)
        if self.debug:
            cv2.imshow('Objects Mask', cv2.resize(objects_mask, None, fx=self.debug_scale, fy=self.debug_scale))
            cv2.waitKey(0)

        # find contours
        contours, _ = cv2.findContours(objects_mask, cv2.RETR_LIST, cv2.CHAIN_APPROX_TC89_L1)
        if self.debug:
            cv2.imshow('Object Contours', cv2.resize(draw_contours_on_image(image=gray, cnts=contours), None, fx=self.debug_scale, fy=self.debug_scale))
            cv2.waitKey(0)
        
        
        # grading
        has_objects_flag = False
        for cnt in contours:
            # get contour cordinates
            (x1,y1), r = cv2.minEnclosingCircle(cnt)
            x, y, w, h = cv2.boundingRect(cnt)
            area = cv2.contourArea(cnt)

            # get r
            radius = min(w, h, r)
            params = self.algo_parasm_obj.Calibration_Coefficients
            # logger.logger("params: "+ str(params))

            ################## pixel to mm transform
            self.algo_parasm_obj.px_value = (params[0]*x1 + params[1]*y1 + params[2]) * 0.92 
            #### diameter
            radius_mm = (radius * self.algo_parasm_obj.px_value)*2 
            # print('Area: ', (np.pi * radius_mm/2 * radius_mm/2))
            # reject those object that arent circular enoug or have size not in desired range
            if area / (np.pi * radius * radius) < self.algo_parasm_obj.circ_acc or not (self.algo_parasm_obj.ranges_dict[0][0]<=radius_mm<self.algo_parasm_obj.ranges_dict[len(self.algo_parasm_obj.ranges_dict.keys())-1][1]):
                continue
            
            has_objects_flag = True

            ###### find radious of equivalent circle
            ### milimeter area of countour
            area_mm = area *  self.algo_parasm_obj.px_value *  self.algo_parasm_obj.px_value
            # print("contour area", area_mm)
            circle_equivalent_r = math.sqrt(area_mm/np.pi)
            # print("circle_equivalent_r", circle_equivalent_r)

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

            self.circle_acc.append(circ_acc)
        


            # grading
            for key in self.algo_parasm_obj.ranges_dict.keys():
                # print("radius_mm : ",radius_mm)
                if self.algo_parasm_obj.ranges_dict[key][0] <= radius_mm < self.algo_parasm_obj.ranges_dict[key][1]:
                    # draw contour on image
                    try:
                        cv2.drawContours(image, [cnt], -1, ImageColor.getcolor(self.algo_parasm_obj.ranges_colors[key], 'RGB'), 3)
                    except:
                        pass
                    # update count
                    self.n_objects+=1
                    # except:
                    #     pass
                    # add to grading arr
                    self.grading_ranges_arr[key]+=self.volume_of_cuntour(circle_equivalent_r, circle_equivalent_r)
                    
        if has_objects_flag:
            # add contours to list
            self.contours_dict[self.image_itr] = contours
            self.image_itr+=1

        if  self.circ_acc_array.sum()!=0:
            self.circ_acc_array = (self.circ_acc_array / self.circ_acc_array.sum()) * 100

        # get ranges percentages
        # if  self.grading_ranges_arr.sum() != 0:
        #     self.grading_ranges_arr = self.grading_ranges_arr / self.grading_ranges_arr.sum() * 100
        
        if self.debug:
            cv2.imshow('Grading Results', cv2.resize(image, None, fx=self.debug_scale, fy=self.debug_scale))
            cv2.waitKey(0)
        print('n_objects: ', self.n_objects)
        
        
        if self.grading_ranges_arr.sum() != 0: 
            return image, (self.grading_ranges_arr / self.grading_ranges_arr.sum()) * 100, self.circ_acc_array, self.n_objects
        else:
            return image, (self.grading_ranges_arr) * 100, self.circ_acc_array, self.n_objects





    