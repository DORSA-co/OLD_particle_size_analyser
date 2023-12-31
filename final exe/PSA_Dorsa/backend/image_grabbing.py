from PyQt5 import QtCore
import numpy as np
import time
from backend import chart
import datetime
TIME_SLEEP = 0.045


class Camera_Image_Grabber_Worker(QtCore.QObject):
    """this class is used as a worker for Qthread to get frame from camera

    :param sQObject: _description_
    :type sQObject: _type_
    """

    finished = QtCore.pyqtSignal()
    show_image = QtCore.pyqtSignal(np.ndarray)
    camera_fps = QtCore.pyqtSignal(str, str)
    

    def assign_parameters(self, ui_obj, camera_obj, show_image=False):
        self.ui_obj = ui_obj
        self.camera_obj = camera_obj
        self.stop = False
        self.show_frames = show_image
    
    
    def grab_frame(self):
        self.ui_obj.images_list.clear()
        while not self.stop:
            try:
                # get frame
                # start = time.time()
                res, frame = self.camera_obj.getPictures()
    
                if not res:
                    continue
                
                if self.ui_obj is not None:
                    self.ui_obj.images_list.append(frame)
                if self.show_frames:
                    self.show_image.emit(frame)

                if self.ui_obj is not None and self.ui_obj.debug:
                    break
                
            except Exception as e:
                print(e)
                continue
            #### calculating FPS
            time.sleep(TIME_SLEEP)
            # end = time.time()
            self.ui_obj.fps = 1/((1/self.camera_obj.get_fps()) + TIME_SLEEP)
            # print('fps: ', self.camera_obj.get_fps())
            
            ####### Sending to label
            self.camera_fps.emit('label_fps', str(round(self.ui_obj.fps, 1)))
        # finish signal
        
        if self.ui_obj is not None:
            self.ui_obj.images_list.clear()
        self.finished.emit()
    


class Image_Process_Worker(QtCore.QObject):
    """this class is used as a worker for Qthread to process frames

    :param sQObject: _description_
    :type sQObject: _type_
    """

    finished = QtCore.pyqtSignal()
    show_image = QtCore.pyqtSignal(np.ndarray)
    update_chart = QtCore.pyqtSignal(np.ndarray, np.ndarray)
    # update_n_detected = QtCore.pyqtSignal(str, str)
    camera_pfs = QtCore.pyqtSignal(str, str)
    #
    
    

    def assign_parameters(self, ui_obj):
        self.ui_obj = ui_obj
        self.stop = False
        self.ui_obj.detection_obj.start_new_detection()
    
    
    def process_frames(self):
        last_grading_infoes = None
        while not self.stop or len(self.ui_obj.images_list)>0:
            # print(len(self.ui_obj.images_list))
            if len(self.ui_obj.images_list)==0:
                continue

            if self.ui_obj.detection_obj.wait_to_save_last_results_flag:
                continue

            try:
                frame = self.ui_obj.images_list.pop(0)
            except:
                continue
            
            self.ui_obj.frame_itr+=1
            
            curr_datetime = datetime.datetime.now().strftime('%Y-%m-%d %H-%M-%S')

            # main detection
            detected_image, grading_infoes, circ_acc, n_objects = self.ui_obj.detection_obj.detect(image=frame)

            # set frame on ui
            self.show_image.emit(detected_image)

            #
            # print(last_grading_infoes, grading_infoes)
            if last_grading_infoes is not None and (last_grading_infoes==grading_infoes).all():
                continue
            else:
                last_grading_infoes = grading_infoes

            
            # # set to chart
            self.update_chart.emit(grading_infoes, circ_acc)

            # set n detected objects
            # self.update_n_detected.emit('n_detected_objects_label', str(n_objects))
            
            self.camera_pfs.emit('label_fps', str(round(self.ui_obj.fps, 1)))

            # print('asd:', last_grading_infoes, grading_infoes)
                
                
        
        # finish signal
        self.finished.emit()
        # self.update_chart.emit(np, circ_acc)