import sqlite3

DATABASE_NAME = 'grading_db'
#
REPORTS_TABLE_NAME = 'reports'
REPORTS_ID = 'id'
REPORTS_DATE = 'date_'
REPORTS_TIME = 'time_'
REPORTS_GRADING_RANGES_DESCRIPTION = 'grading_ranges_description'
REPORTS_PERCENTAGES = 'reports_percentages'
REPORTS_SAVE_PATH = 'save_path'
#

CAMERA_TABLE_NAME = 'camera_settingss'
CAMERA_ID = 'id'
CAMERA_SERIAL = 'serial'
CAMERA_EXPOSURE = 'exposure'
CAMERA_GAIN = 'gain'
CAMERA_TRIGGER_MODE = 'trigger'
#
ALGO_TABLE_NAME = 'algo_params'
ALGO_DESCRIPTION = 'description'
ALGO_MIN_CIRCULARITY = 'min_circularity'
ALGO_BLUR_KSIZE = 'blur_ksize'
ALGO_GRAY_THRS = 'gray_thrs'
ALGO_IS_DEFAULT = 'is_default'
#
RANGES_TABLE_NAME = 'grading_rangess'
RANGES_ID = 'id'
RANGES_DESCRIPTION = 'description'
RANGES_RANGES = 'ranges'
RANGES_IS_DEFAULT = 'is_default'

##### users table parameters
USERS_TABLE_NAME = 'users'
USERS_ID = 'id'
USERS_USERNAME = 'username'
USERS_PASSWORD = 'password'
USERS_ACCESS_LEVEL = 'access_level'

class sqlite_database():

    def __init__(self, name):
        self.name = name
        self.database_connection_flag = False
        
    def connect(self):
        ###### creat database
        self.database_connection = sqlite3.connect(self.name + ".db")
        self.database_cursor = self.database_connection.cursor()
        self.database_connection_flag = True


    def creat_table(self, table_name, cols):
        try:
            args = "("
            for i,col in enumerate(cols):
                if i != len(cols)-1:
                    args = args + col + ","
                else:
                    args = args + col
            
            args = args + ")"
            self.database_cursor.execute("CREATE TABLE " + table_name + args)
        except:
            pass

    def add_record(self, data, table_name, parametrs):
        args = "("
        for i,d in enumerate(data):
            if i != len(data)-1:
                args = args + "'%s'" % d + ","
            else:
                args = args + "'%s'" % d
        args = args + ")"
        columns = "("
        for i,col in enumerate(parametrs):
            if i != len(parametrs)-1:
                columns = columns + col + ","
            else:
                columns = columns + col
        columns = columns + ")"



        if self.database_connection_flag:
            # input query
            insert_query = """INSERT INTO {} {} 
                                VALUES 
                                {} """.format(table_name, columns, args)
            
            # execute query with input data
            self.database_cursor.execute(insert_query)
            self.database_connection.commit()
            return True


    def remove_record(self, col_name, id, table_name):
        try:
            if self.database_connection_flag:
                delete_query = """DELETE FROM {} WHERE {}={};""".format(table_name,col_name,"'"+id+"'")
                self.database_cursor.execute(delete_query)
                self.database_connection.commit()

                return True
            
            else:
                return False
        
        except Exception as e:
            print(e)
            return False


    def update_record(self, table_name, col_name, value, id, id_value):
        try:
            if self.database_connection_flag:
                mySql_insert_query = """UPDATE {} 
                                    SET {} = {}
                                    WHERE {} ={} """.format(table_name, col_name, ("'"+value+"'"),id, ("'"+id_value+"'") if isinstance(id_value, str) else id_value)
                
                self.database_cursor.execute(mySql_insert_query)
                self.database_connection.commit()

                return True
            
            else:
                return False
        
        except Exception as e:
            # print(e)
            return False
    

    def update_column(self, table_name, searching_col_name, searching_value, col_name, value):
        try:
            sql_query = "UPDATE %s SET %s = '%s' WHERE %s = '%s'" % (table_name, col_name, value, searching_col_name, searching_value)
            self.database_cursor.execute(sql_query)
            self.database_connection.commit()
            return True
        
        except:
            return False
    

    def update_colomn_for_all_items(self, table_name, col_name, value):
        try:
            self.database_cursor.execute("UPDATE %s SET %s = '%s' " % (table_name, col_name, value))
            self.database_connection.commit()
            return True
        
        except:
            return False
        


    def search_in_table(self):
        return

    def retrive_all(self, table_name):
        try:
            self.database_cursor.execute("SELECT * from %s" % (table_name))
            records = self.database_cursor.fetchall()
            col_names = [col[0] for col in self.database_cursor.description]
            
            res = []
            for record in records:
                record_dict = {}
                for i in range( len(col_names) ):
                    record_dict[col_names[i]] = record[i]
                res.append(record_dict)

            return True, res

        except:
            return False, []


    def delete_table(self, table_name):
        try:
            self.database_cursor.execute("DROP TABLE %s" % (table_name))
            return True
        
        except:
            return False
    

    def create_default_tables(self):
        # reports table
        self.creat_table(table_name=REPORTS_TABLE_NAME, cols=[REPORTS_ID, REPORTS_DATE, REPORTS_TIME, REPORTS_GRADING_RANGES_DESCRIPTION, REPORTS_PERCENTAGES,REPORTS_SAVE_PATH])

        # camera settings table
        self.creat_table(table_name=CAMERA_TABLE_NAME, cols=[CAMERA_ID, CAMERA_SERIAL, CAMERA_EXPOSURE, CAMERA_GAIN, CAMERA_TRIGGER_MODE])

        # algorithm params table
        self.creat_table(table_name=ALGO_TABLE_NAME, cols=[ALGO_DESCRIPTION, ALGO_BLUR_KSIZE, ALGO_MIN_CIRCULARITY, ALGO_GRAY_THRS, ALGO_IS_DEFAULT])

        # ranges table
        self.creat_table(table_name=RANGES_TABLE_NAME, cols=[RANGES_ID, RANGES_DESCRIPTION, RANGES_RANGES, RANGES_IS_DEFAULT])

        ##### users table
        self.creat_table(table_name=USERS_TABLE_NAME, cols=[USERS_ID, USERS_USERNAME, USERS_PASSWORD, USERS_ACCESS_LEVEL])



if __name__ == '__main__':
    class_obj = sqlite_database("grading_db")
    class_obj.connect()
    # class_obj.creat_table(table_name=REPORTS_TABLE_NAME, cols=[REPORTS_ID, REPORTS_DATE, REPORTS_TIME, REPORTS_GRADING_RANGES_DESCRIPTION, REPORTS_PERCENTAGES,REPORTS_SAVE_PATH])
    # class_obj.creat_table("test_table", ["t1", "t2", "t3"])
    # class_obj.add_record(['1', 'dorsa-co', 'Dorsa@1400', '[1, 1, 1, 1, 1]'], USERS_TABLE_NAME, [USERS_ID, USERS_USERNAME, USERS_PASSWORD, USERS_ACCESS_LEVEL])
    # class_obj.add_record(["4","5","6"], "test_table", ["t1", "t2", "t3"], 3)
    # class_obj.add_record(["7","8","9"], "test_table", ["t1", "t2", "t3"], 3)
    # class_obj.remove_record("t1", 4, "test_table")
    # class_obj.database_cursor.execute("SELECT * from reports")
    # print(class_obj.database_cursor.fetchall())

    # print(class_obj.retrive_all(table_name=CAMERA_TABLE_NAME))
    # print(class_obj.delete_table(table_name=REPORTS_TABLE_NAME))
    # class_obj.update_colomn_for_all_items(table_name=ALGO_TABLE_NAME, col_name=ALGO_IS_DEFAULT, value=False)

    # class_obj.remove_record(col_name=CAMERA_ID, id='0', table_name=CAMERA_TABLE_NAME)
