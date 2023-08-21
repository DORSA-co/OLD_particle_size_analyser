# from camera import Collector
import threading
from PyQt5.QtGui import QIcon as sQIcon
from PyQt5.QtGui import QImage as sQImage
from PyQt5.QtGui import QPixmap as sQPixmap 
from PyQt5 import QtCore
import cv2
from functools import partial
from backend import camera_connection, camera_settings, image_grabbing, database

class calibration_class():
    def __init__(self, ui_obj):
        self.ui_obj = ui_obj
        self.camera = None
        self.camera_connect_flag = False
        self.debug_calibration_flag = self.ui_obj.checkBox_calib.isChecked()
        self.camera_params = {'gain_value': 0, 'expo_value': 115, 'trigger_mode': '0', 'serial_number': '23804186'}
        self.frame_to_detect = None
    # connect to camera

    
    def connect_func(self):
        # not connected to camers, try to connect
        if not self.camera_connect_flag:
            self.camera = None
            # check if cameras are connected to network
            self.ui_obj.comboBox_SerialNumber.clear()
            try:
                # print("here")
                collector = camera_connection.Collector(serial_number='', list_devices_mode=True)
                serial_list = collector.serialnumber()
                # print("test",serial_list)

                self.ui_obj.comboBox_SerialNumber.addItem(str(serial_list[0]))
                del collector

                # first camera
                # print(self.camera_params)
                if self.camera_params[database.CAMERA_TRIGGER_MODE] == '0':
                    triggerMode = False
                elif self.camera_params[database.CAMERA_TRIGGER_MODE] == '1':
                    triggerMode = True
                self.camera =camera_connection.Collector(serial_number=self.camera_params[database.CAMERA_SERIAL], 
                                                            gain=self.camera_params[database.CAMERA_GAIN], 
                                                            exposure=self.camera_params[database.CAMERA_EXPOSURE],
                                                            max_buffer=20,
                                                            trigger=triggerMode, 
                                                            delay_packet=6, 
                                                            packet_size=1500, 
                                                            frame_transmission_delay=0, 
                                                            width=2448,
                                                            height=2048, 
                                                            offet_x=0, 
                                                            offset_y=0,
                                                            manual=True, 
                                                            list_devices_mode=False, 
                                                            trigger_source='Software')
     
                res, _ = self.camera.start_grabbing()
                print('res: ', res)
                if res:

                    self.camera_connect_flag = True
                    # change camera-connect states
                    self.ui_obj.camera_calib_btn.setStyleSheet('QPushButton{border-right: 8px solid green;}')
                    self.show_mesagges(label_name=self.ui_obj.msg_label_2, text='Camera connected successfully', color='green')
                    # make get picture button available
                    self.ui_obj.calib_btn.setEnabled(True)
                    self.start_capturing()
                    # self.frame_to_detect = frame
                    # self.ui_obj.set_image_on_label_calib(frame, False)
                else:
                    print("error start grabbing")
            # error in connecting to cameras
            except Exception as e:
                print(e)
                self.ui_obj.camera_calib_btn.setStyleSheet('QPushButton{border-right: 8px solid red;}')
                self.show_mesagges(label_name=self.ui_obj.msg_label_2, text='Failed to connect to camera', color='red')

        # connected to cameras, try to dissconnect
        else:            
            # dissconnect camera
            # if len(self.cameras) > 0:
            self.camera.stop_grabbing()
            self.camera = None
            self.camera_worker.stop = True
            # change camera-connect states
            # self.stop_capturing()
            self.camera_connect_flag = False
            self.ui_obj.camera_calib_btn.setStyleSheet('QPushButton{border-right: 8px solid red;}')
            self.ui_obj.calib_btn.setEnabled(False)
            self.ui_obj.camera_calib_btn.setEnabled(True)
            
            
            # self.set_image_to_ui(label_name=self.ui_obj.camera_live_label_2, image=None, no_image=True)
            # change camera-connect button text
            
            self.ui_obj.camera_calib_btn.setStyleSheet('QPushButton{border-right: 8px solid red;}')
            # message
            self.show_mesagges(label_name=self.ui_obj.msg_label_2, text='Camera disconnected successfully', color='green')
            # self.update_ui_labels(label=self.ui_obj.camera_connect_label_2, state=False)
            # self.update_charts(clear=True)
        
            

    # get frame from cameras
    def get_picture(self):

        # if self.capture_flag:
        try:
            camera_frame = self.camera.getPictures()
            self.camera_frame = camera_frame
            print("frame ",self.camera_frame )
            return camera_frame
        except:
            self.show_mesagges(label_name=self.ui_obj.msg_label_2, text='connection failed', color='red')

    def start_capturing(self):

        # Create frame grabbing worker
        self.camera_worker = image_grabbing.Camera_Image_Grabber_Worker()
        self.camera_worker.assign_parameters(ui_obj=self.ui_obj, camera_obj=self.camera, show_image=True)
        # Create QThread object
        self.camera_thread = QtCore.QThread()
        # assign worker to the thread
        self.camera_worker.moveToThread(self.camera_thread)
        # Connect signals and slots
        self.camera_worker.show_image.connect(partial(self.set_camera_frame_on_calibration))
        self.camera_worker.camera_fps.connect(partial(self.ui_obj.set_text_on_label))
        self.camera_thread.started.connect(partial(self.camera_worker.grab_frame))
        self.camera_worker.finished.connect(partial(self.camera_thread.quit))
        self.camera_thread.finished.connect(partial(self.camera_thread.deleteLater))
        self.camera_thread.start()

        self.ui_obj.calib_btn.setEnabled(True)
       
        # res, frame = self.get_picture()
        
        # return frame
        
    def set_camera_frame_on_calibration(self, frame):
        self.frame_to_detect = frame
        self.ui_obj.set_image_on_label_calib(frame, False)


    # stop frame grabbing
    def stop_capturing(self):
        self.camera_connect_flag = False
        self.calibration_flag = False
        self.ui_obj.calib_btn.setEnabled(False)

    # update UI flag indicator labels
    def update_ui_labels(self, label, state=False):
        if state:
            label.setStyleSheet('background-color: green;')
        else:
            label.setStyleSheet('background-color: red;')


    # show messages on UI
    def show_mesagges(self, label_name, text, color='green'):
        name=label_name
        if text != None:
            label_name.setText(text)
            label_name.setStyleSheet("color:{}".format(color))       
            threading.Timer(2, self.show_mesagges, args=(name,None)).start()
        else:
            label_name.setText('')


    # set cameras imnages to UI
    def set_image_to_ui(self,label_name, image, no_image=False):
        try:
            if no_image:
                image = cv2.imread('icons/no_image.png')
            h, w, ch = image.shape
            bytes_per_line = ch * w
            convert_to_Qt_format = sQImage(image.data, w, h, bytes_per_line, sQImage.Format_BGR888)
            label_name.setPixmap(sQPixmap.fromImage(convert_to_Qt_format))
        except:
            pass
