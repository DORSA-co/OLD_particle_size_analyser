import database

from backend import texts, database_info



class dataBaseUtils():
    """this class is used as an API to work with database
    """
    
    def __init__(self, logger_obj=None) :
        self.db = database.dataBase(database_info.USERNAME, database_info.PASSWORD, database_info.LOCALHOST, database_info.SCHEMA_NAME, logger_obj=logger_obj)
        
        # logger object
        self.logger_obj = logger_obj
    

    def get_log(self, message='nothing', level=1):
        """this function is used to get log from database tasks

        :param message: _description_, defaults to 'nothing'
        :param level: _description_, defaults to 1
        """

        if self.logger_obj != None:
            self.logger_obj.create_new_log(message=message, level=level)


    def load_cam_params(self, input_camera_id):
        """this function is used to load camear parameters from camera tables, using the camera id

        :param input_camera_id: _description_
        :return: _description_
        """
        
        try:
            record = self.db.search(table_name=database_info.CAMERA_PARAMS_TABLE, param_name=database_info.CAMAERA_ID, value=input_camera_id)[0]
            self.get_log(message='%s %s: %s' % (texts.MESSEGES['db_load_cam_params']['en'], texts.TITLES['camera_id']['en'], input_camera_id))
            return True, record

        except Exception as e:
            self.get_log('%s %s: %s' % (texts.ERRORS['db_load_cam_params_failed']['en'], texts.TITLES['camera_id']['en'], input_camera_id), level=5)
            return False, []
    

    def update_cam_params(self, input_camera_id, input_camera_params):
        """this function is used to update camera params of input camera id on table

        :param input_camera_id: _description_
        :param input_camera_params: _description_
        :return: _description_
        """
        
        try:
            for camera_param in input_camera_params.keys():
                self.db.update_record(table_name=database_info.CAMERA_PARAMS_TABLE,
                                        col_name=camera_param,
                                        value=str(input_camera_params[camera_param]),
                                        id=database_info.CAMAERA_ID,
                                        id_value=input_camera_id)
            
            self.get_log(message='%s %s: %s' % (texts.MESSEGES['db_update_cam_params']['en'], texts.TITLES['camera_id']['en'], input_camera_id))
            return True

        except:
            self.get_log(message='%s %s: %s' % (texts.ERRORS['db_update_cam_params_failed']['en'], texts.TITLES['camera_id']['en'], input_camera_id), level=5)
            return False
    

    def search_camera_by_serial(self, input_camera_serial):
        """this function is used to search camera by its serial

        :param input_camera_serial: _description_
        :return: _description_
        """

        try:
            record = self.db.search(table_name=database_info.CAMERA_PARAMS_TABLE, param_name=database_info.CAMERA_SERIAL, value=input_camera_serial)

            if len(record)>0:
                record = record[0]
                self.get_log(message='%s %s: %s - %s: %s' % (texts.MESSEGES['db_camera_found_by_serial']['en'], texts.TITLES['camera_id']['en'],
                                                            record[database_info.CAMAERA_ID], texts.TITLES['camera_serial']['en'], input_camera_serial))
                return True, record
            
            else:
                self.get_log(message='%s %s: %s' % (texts.WARNINGS['db_no_camera_found_by_serial']['en'], texts.TITLES['camera_serial']['en'], input_camera_serial), level=2)
                return False, []
                
        except Exception as e:
            return False, []