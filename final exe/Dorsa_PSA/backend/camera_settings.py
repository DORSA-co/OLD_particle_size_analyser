import numpy as np
import cv2
import time
import os
from PySide6.QtGui import QStandardItem as sQStandardItem
from backend import camera_connection, texts, database


# raw image address for ui labels
raw_image_path = './images/no_image.png'

# number of cameras
num_cameras = 1

# camera ids
all_camera_ids = ["{:02d}".format(x) for x in np.arange(1, num_cameras+1)]
top_camera_ids = ["{:02d}".format(x) for x in np.arange(1, num_cameras//2+1)]
bottom_camera_ids = ["{:02d}".format(x) for x in np.arange(num_cameras//2+1, num_cameras+1)]

# guidance grids for camera calibration
grid_shape = [20, 30]
crosshair_shape = [2 ,2]
grid_color = (255 ,0 , 0)
grid_thickness = 1

NO_SERIAL = 'No Serial'
TRIGGER_SOURCE = ['Off', 'Software', 'Line1']
GET_FRAME_EVERY = 0.1 # in second

# camer calibration  elements names in ui
calibration_params = ['calib_rotate_spinbox', 'calib_shiftw_spinbox', 'calib_radio_corsshair', 'calib_radio_grid', 'calib_shifth_spinbox'\
                        ,'calib_take_image', 'pixelvalue_next_btn', 'pixelvalue_prev_btn', 'calib_minarea_spinbox', 'calib_maxarea_spinbox', 'calib_maxarea_spinbox'\
                        , 'calib_thrs_spinbox', 'calibration_zoomin', 'calibration_zoomout', 'zoomin_label', 'zoomout_label']

#---------------------------------------------------------------------------------------------------------------------------

    
# get camera id by camera name label in the UI
def get_camera_id(camera_name_label):
    """
    this function is used to get camera id, using camera name label in ui camera settings page

    Inputs:
        camera_name_label: in string
    
    Returns:
        camera_id: in string
    """
    
    try:
        return str(int(camera_name_label[-2:]))
    except:
        return '0'


# camera parametrs in camera setting section
#---------------------------------------------------------------------------------------------------------------------------
# get camera parameters from UI
def get_camera_params_from_ui(ui_obj):
    """
    this function is used to get camera parameters from ui (camera settings page)

    Inputs:
        ui_obj: main ui object

    Returns:
        camera_params
    """
    
    camera_params = {}
    camera_params[database.CAMERA_GAIN] = ui_obj.Gain_ratio_2.value()
    camera_params[database.CAMERA_EXPOSURE] = ui_obj.exposure_time.value()
    # trigger mode
    camera_params[database.CAMERA_TRIGGER_MODE] = str(ui_obj.comboBox_TriggerMode.currentIndex())
    # serial number
    camera_params[database.CAMERA_SERIAL] = '0' if ui_obj.comboBox_SerialNumber.currentText()==NO_SERIAL else ui_obj.comboBox_SerialNumber.currentText()

    return camera_params


# set/show current camera parameters on UI
def set_camera_params_to_ui(ui_obj, db_obj, camera_params, camera_id, available_serials):
    """
    this function is used to set input camera params to ui (camera settings page)

    Inputs:
        ui_obj: main ui object
        db_obj: main database object
        camera_params: input camera parameters (in dict)
        camera_id: input camera id (in string)
        available_serials: available camera serials (list of strings)
    
    Returns: None
    """
    ui_obj.Gain_ratio_2.setValue(camera_params['gain_value'])
    ui_obj.exposure_time.setValue(camera_params['expo_value'])
    # trigger mode
    ui_obj.comboBox_TriggerMode.setCurrentIndex(int(camera_params['trigger_mode']))

    # serial
    assign_existing_serials_to_ui(ui_obj, db_obj, camera_id, available_serials)
    set_camera_serial_to_ui(ui_obj, camera_params['serial_number'])


def set_camera_serial_to_ui(ui_obj, assigned_serial):
    """
    this function takes as input a camera serial and update the serial combobox current value

    Inputs:
        ui_obj: main ui object
        assigned_serial: camera serial (in string)

    Returns: None

    """
    # no serial is asigned to current camera
    if assigned_serial == '0':
        ui_obj.comboBox_SerialNumber.setCurrentText(NO_SERIAL)

    # serial asigned to current camera
    else:
        ui_obj.comboBox_SerialNumber.setCurrentText(assigned_serial)
        

# 
def assign_existing_serials_to_ui(ui_obj, db_obj, camera_id, available_serials):
    """
    this function is called on every camera selection on camera settngs page,
    it takes as input available camera serials list, and current camera id, and those serial that not assigned to any camera, and the current camera serial
    are added to serial combobox on ui

    Inputs:
        ui_obj: main ui object
        db_obj: database object
        camera_id: current camera id
        available_serials: list of available camera serals (list of strings)
    
    returns: None
    """
    
    # clear all items in combo
    ui_obj.comboBox_SerialNumber.clear()

    # assign no serial label
    item = sQStandardItem(NO_SERIAL)
    ui_obj.comboBox_SerialNumber.model().appendRow(item)

    for serial in available_serials:
        # validating serial to be not used by another camera
        serial_info = db_obj.search_camera_by_serial(serial)

        # add serial to combo, if not assigned to any camera, or is assigned to current camera
        if len(serial_info) == 0 or (len(serial_info) != 0 and serial_info['id'] == int(camera_id)):
            item = sQStandardItem(serial)
            ui_obj.comboBox_SerialNumber.model().appendRow(item)


# set cameras parameters to database given single camera-id (or for multiple cameras given multiple cameras-ids)
def set_camera_params_from_ui_to_db(ui_obj):
    """
    this function is used to update camera params on database, given camera id(s)

    Inputs:
        db_obj: database object
        camera_id: current camera id (in string)
        camera_params: dict of camera params
        checkbox_values: value of camera select checkboxes determing wheareas apply setting to current camera only or to multiple cameras
    
    Returns:
        result: a boolean value determining if the settings are applied to database or not
    """

    camera_params = get_camera_params_from_ui(ui_obj=ui_obj)

    # delete last record in table
    ui_obj.db.remove_record(col_name=database.CAMERA_ID, id='0', table_name=database.CAMERA_TABLE_NAME)

    # apply settings to single current camera
    ui_obj.db.add_record(data=[0, '0', camera_params[database.CAMERA_EXPOSURE], camera_params[database.CAMERA_GAIN], camera_params[database.CAMERA_TRIGGER_MODE]], table_name=database.CAMERA_TABLE_NAME, parametrs=[database.CAMERA_ID, database.CAMERA_SERIAL, database.CAMERA_EXPOSURE, database.CAMERA_GAIN, database.CAMERA_TRIGGER_MODE])

    
    

# get cameras parameters from database given camera-id
def get_camera_params_from_db_to_ui(db_obj, ui_obj):
    """
    this function is used to get camera params from database, using camera id

    Inputs:
        db_obj: database object
        camera_id: id of the camera (in string)
    
    Returns:
        camera_params: a dict containing camera parameters
    """
    
    res, camera_params = db_obj.retrive_all(table_name=database.CAMERA_TABLE_NAME)

    if res and len(camera_params)>0:
        camera_params = camera_params[0]
        # print('here' , camera_params)
        ui_obj.exposure_time.setValue(int(camera_params[database.CAMERA_EXPOSURE]))
        ui_obj.Gain_ratio_2.setValue(int(camera_params[database.CAMERA_GAIN]))
        ui_obj.comboBox_TriggerMode.setCurrentIndex(int(camera_params[database.CAMERA_TRIGGER_MODE]))

    


# validating camera ip address
def validate_camera_ip(ui_obj, db_obj, camera_id, camera_params): # must change to validate ip range
    """
    this function is used to validate camera ip to be valid and not used by oter cameras

    Inputs:
        ui_obj: main ui object
        db_obj: database object
        camera_id: current camera ip
        camera_params: camera parameters (dict)

    Returns:
        result: a boolean determining ip validation is ok or not
        message: the error message of ip validation not ok
    """
    
    # validating ip address to be in correct form
    ip_validate = ip_validation(ui_obj, camera_params['ip_address'])
    if ip_validate != 'True':
        return False, ip_validate

    # validating ip address to be not used by another camera
    ip_info = db_obj.search_camera_by_ip(camera_params['ip_address'])

    if len(ip_info) != 0 and ip_info['id'] != int(camera_id):
        return False, texts.ERRORS['ip_in_used'][ui_obj.language]

    return True, 'True'


def ip_validation(ui_obj, ip_address):
    """
    this function is used to validate ip to be in right format

    Inputs:
        ui_obj: main ui object
        ip_address: input ip address (in string)
    
    Rrturns:
        message: a text message determining if the ip validation is ok or not,
            'True' for validation ok
    """
    
    octets = ip_address.split(".")
    size = len(octets)
    # check to have 4 sections
    if size != 4:
        return texts.WARNINGS['ip_invalid'][ui_obj.language]

    # check each section to be in range 0-256
    for octet in octets:
        try:
            number = int(octet)
            if number < 0 or number > 255:
                return texts.WARNINGS['ip_out_of_range'][ui_obj.language]
        except:
            return texts.WARNINGS['ip_contain_letters'][ui_obj.language]

    return 'True'



# soft-calibration in calibration settings page
#---------------------------------------------------------------------------------------------------------------------------
# get camera calibration parameters from UI
def get_camera_calibration_params_from_ui(ui_obj):
    """
    this function returns the camera sot calibration params from ui

    Inputs:
        ui_obj: main ui object
    
    Returns:
        camera_calibration_params: in dict
    """
    
    camera_calibration_params = {}
    camera_calibration_params['calib_minarea'] = ui_obj.calib_minarea_spinbox.value()
    camera_calibration_params['calib_maxarea'] = ui_obj.calib_maxarea_spinbox.value()
    camera_calibration_params['calib_thrs'] = ui_obj.calib_thrs_spinbox.value()
    camera_calibration_params['pxvalue_a'] = ui_obj.pxvaluea_label.text()
    camera_calibration_params['pxvalue_b'] = ui_obj.pxvalueb_label.text()
    camera_calibration_params['pxvalue_c'] = ui_obj.pxvaluec_label.text()

    return camera_calibration_params


# set camera calibration parameters to UI
def set_camera_calibration_params_to_ui(ui_obj, camera_calibration_params):
    """
    this functino is used to set camera calibration params returned from dataabse, to ui

    Args:
        ui_obj (_type_): main ui object
        camera_calibration_params (_type_): in dict
    
    Returns: None
    """

    ui_obj.calib_rotate_spinbox.setValue(camera_calibration_params['rotation_value'])
    ui_obj.calib_shifth_spinbox.setValue(camera_calibration_params['shifth_value'])
    ui_obj.calib_shiftw_spinbox.setValue(camera_calibration_params['shiftw_value'])


# set calibration parameters of the camera to database 
def set_camera_calibration_params_to_db(db_obj, camera_id, camera_calibration_params):
    """
    this function is used to set camera calibration params to database

    Args:
        db_obj (_type_): database object
        camera_id (_type_): _description_
        camera_calibration_params (_type_): in dict

    Returns:
        resault: boolean determining update ok
    """

    res = db_obj.update_cam_params(str(int(camera_id)), camera_calibration_params)
    return res # validation


# get/load calibration parameters of the camera from database 
def get_camera_calibration_params_from_db(db_obj, camera_id):
    """
    this function is used to get camera calibration params from database, given camera id

    Args:
        db_obj (_type_): database object
        camera_id (_type_): _description_

    Returns:
        camera_calibration_params: in dict
    """

    camera_calibration_params = db_obj.load_cam_params(str(int(camera_id)))
    return camera_calibration_params


# soft calibration functions
def shift_calibration_image(image, shifth, shiftw):
    """
    this function is used to shift image along y or x (vertical or horizintal)

    Inputs:
        image: input image
        shifth: value to shift image horiintaly
        shiftw: value to shift image vertically
    
    Returns:
        shifted_image:
    """
    
    row, col = image.shape[:2]
    translation_matrix = np.float32([[1, 0, shiftw], [0, 1, shifth]])   
    shifted_image = cv2.warpAffine(image, translation_matrix, (col, row))

    return shifted_image


def rotate_calibration_image(image, angle):
    """
    this function is used to rotate image along center by input angle

    Inputs:
        image: input image
        angle: input angle to rotate image (in degree)
    
    Returns:
        rotated_image:
    """
    
    row, col = image.shape[:2]
    center = (col / 2, row / 2)
    rot_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated_image = cv2.warpAffine(image, rot_matrix, (col, row))

    return rotated_image


# draw guidance grid on the calibration image
def draw_grid(image, crosshair=True):
    """
    this function is used to draw align grids on input image

    Args:
        image (_type_): _description_
        crosshair (bool, optional): a boolean determining wheather draw cross-hair or grid. Defaults to True.

    Returns:
        image: image with grid
    """
    row, col = image.shape[:2]
    rows, cols = crosshair_shape if crosshair else grid_shape
    dy, dx = row / rows, col / cols
    # draw vertical lines
    for x in np.linspace(start=dx, stop=col-dx, num=cols-1):
        x = int(round(x))
        cv2.line(image, (x, 0), (x, row), color=grid_color, thickness=grid_thickness)
    # draw horizontal lines
    for y in np.linspace(start=dy, stop=row-dy, num=rows-1):
        y = int(round(y))
        cv2.line(image, (0, y), (col, y), color=grid_color, thickness=grid_thickness)

    return image


# # apply soft-calibration parameters on input image
# def apply_soft_calibrate_on_image(ui_obj, image, camera_calibration_params, pxcalibration=False):
#     """
#     this function is used to apply soft calibration params to camera image

#     Inputs:
#         ui_obj: main ui object
#         image: input camera image
#         camera_calibration_params: input camera calibration params (as a dict)
#         pxcalibration:  a boolean determining wheater in pixel calibration step or not

#     Returns:
#         image: result image that is soft calibrated
#     """
    
#     # rotating and calibrating image
#     image = rotate_calibration_image(image, camera_calibration_params['rotation_value'])
#     image = shift_calibration_image(image, camera_calibration_params['shifth_value'], camera_calibration_params['shiftw_value'])

#     # check to show/not show guidance grid on image, if on pixel value calibration step
#     if not pxcalibration:
#         if ui_obj.calib_radio_corsshair.isChecked():
#             image = draw_grid(image, crosshair=True)
#         elif ui_obj.calib_radio_grid.isChecked():
#             image = draw_grid(image, crosshair=False)
            
#     return image





def get_available_cameras_list_serial_numbers():
    """
    this function is used to get available camera serials that are connected to network

    Returns:
        serial_list: list of available camera serials (in string)
    """
    # camera collector object
    collector = camera_connection.Collector(serial_number='0', list_devices_mode=True)
    # get serial number of available cameras
    serial_list = collector.serialnumber()
    #
    del collector

    return serial_list


def update_available_camera_serials_on_db(db_obj, available_serials):
    """
    this function is used to update available camera serials on database,
    it takes as input available camera serial, and checks the database,
    for each camera, if serial in database not in available cameras, assign 0 as its serial

    Args:
        db_obj (_type_): database object
        available_serials (_type_): list of available camera serials (in string)

    Returns: None
    """

    for camera_id in all_camera_ids:
        # get camera serials
        serial_number = get_camera_params_from_db(db_obj, str(int(camera_id)))['serial_number']
        if serial_number not in available_serials and serial_number!='0':
            res = db_obj.update_cam_params(str(int(camera_id)), {'serial_number':'0'})





def show_cameras_summary(ui_obj):
    """
    this function is used to set/update cameras summary params on ui dashboard page

    Args:
        ui_obj (_type_): main ui object
    
    Returns: None
    """

    try:

        # n available cameras
        n_available_camera = len(get_available_cameras_list_serial_numbers())
        if n_available_camera == num_cameras:
            ui_obj.show_mesagges(ui_obj.available_cameras, text=str(n_available_camera), level=0, clearable=False, prefix=False)
        
        elif n_available_camera > 0:
            ui_obj.show_mesagges(ui_obj.available_cameras, text=str(n_available_camera), level=1, clearable=False, prefix=False)
        
        else:
            ui_obj.show_mesagges(ui_obj.available_cameras, text=str(n_available_camera), level=2, clearable=False, prefix=False)

        # cameras trigger mode
        ui_obj.show_mesagges(ui_obj.dash_trigger_mode, text=TRIGGER_SOURCE[2], level=0, clearable=False, prefix=False)
    
    except Exception as e:
        ui_obj.logger.create_new_log(message=texts.WARNINGS['camera_summary_failed']['en'], level=5)
        return



    




    


    





    
    





    


    
        