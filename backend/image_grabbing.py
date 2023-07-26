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

            time.sleep(TIME_SLEEP)

        
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
    update_n_detected = QtCore.pyqtSignal(str, str)
    

    def assign_parameters(self, ui_obj):
        self.ui_obj = ui_obj
        self.stop = False
        self.ui_obj.detection_obj.start_new_detection()
    
    
    def process_frames(self):
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
            # print(grading_infoes.shape)
            # writer =  pd.ExcelWriter(r'Excel/Grading_Resualt.xlsx')

            # grading_infoes_pd = pd.DataFrame(grading_infoes)
            # circ_acc_pd = pd.DataFrame(circ_acc)
            # n_objects_pd = pd.DataFrame(n_objects)


            # grading_infoes_pd.to_excel(writer,sheet_name = 'grading infoes',index='False')
            # circ_acc_pd.to_excel(writer,sheet_name = 'circ acc',index='False')
            # n_objects_pd.to_excel(writer,sheet_name = 'number of objects',index='False')

            # writer.save()



            # set frame on ui
            self.show_image.emit(detected_image)

            # # set to chart
            self.update_chart.emit(grading_infoes, circ_acc)

            # set n detected objects
            self.update_n_detected.emit('n_detected_objects_label', str(n_objects))


            # print(len(self.ui_obj.images_list))

            # time.sleep(0.04)
            # cv2.imwrite('frames/%s.jpg' % (self.ui_obj.frame_itr), detected_image)

            # print('sdfsd')
                
                
        
        # finish signal
        self.finished.emit()