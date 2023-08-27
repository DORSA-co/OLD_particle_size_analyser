from PyQt5 import QtWidgets, QtCore, QtGui
from functools import partial

from backend import texts, database

ICON_PATHES = './Icons/'


class Users():
    """this class is used to manage system users
    """

    def __init__(self):
        self.users_list = []
    

    def get_count(self):
        return len(self.users_list)
    

    def get_all_users_list(self):
        """this function is used to get all users
        """

        try:
            return True, self.users_list
        except:
            return False, []
    

    def set_all_users(self, users_list):
        """this function is used to set all users to list
        """

        self.users_list = users_list
    

    def get_user_by_username(self, username):
        """this function is used to get user info belonging to a user

        :param username: _description_
        """

        try:
            print(len(self.users_list))
            for i in range(len(self.users_list)):
                
                if self.users_list[i][database.USERS_USERNAME] == username:
                    print(self.users_list[i][database.USERS_USERNAME])
                    return True, self.users_list[i]
            
            return False, []
        
        except Exception as e:
            print(e)
            return False, []


    def add_new_user(self, user_info):
        """this function is used to add new user to users list

        :param user_info: _description_
        """

        try:
            self.users_list.append(user_info)
            return True
        except:
            return False

    
    def update_existing_user(self, user_info):
        """this function is used to update existing user info

        :param user_info: _description_
        """

        try:
            for i in range(len(self.users_list)):
                if self.users_list[i][database.USERS_USERNAME] == user_info[database.USERS_USERNAME]:
                    self.users_list[i] = user_info
                    return True
        
        except:
            return False
    

    def delete_user(self, user_name):
        """this function is used to delete an existing user

        :param user_info: _description_
        :return: _description_
        """

        try:
            for i in range(len(self.users_list)):
                if self.users_list[i][database.USERS_USERNAME] == user_name:
                    self.users_list.pop(i)
                    return True
        
        except:
            return False



# validate new user username
def new_user_info_validation(ui_obj, users_list_obj, user_info, modify_user=False):
    """this function is used to validate new user info, to be in right format and be unique

    :param ui_obj: _description_
    :param db_obj: _description_
    :param user_info: _description_
    :return: _description_
    """

    # check fields not empty
    if user_info[database.USERS_PASSWORD] == '' or user_info[database.USERS_USERNAME] == '':
        ui_obj.show_message('massage_signin_label', text=texts.WARNINGS['fields_empty'][ui_obj.language], level=1)
        return False

    # check username to be unique
    if not modify_user:
        res, users_list = users_list_obj.get_all_users_list()
        if not res:
            return False
        #
        for user in users_list:
            if user[database.USERS_USERNAME].lower() == user_info[database.USERS_USERNAME].lower():
                ui_obj.show_message('massage_signin_label',text=texts.WARNINGS['username_duplicate'][ui_obj.language], level=2)
                return False
        
    return True


# def create_users_table(ui_obj):
#     """this function is used to create users table

#     :param ui_obj: _description_
#     :param change_row_count_only: _description_, defaults to False
#     """

#     # assign heders
#     ui_obj.users_table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)
#     ui_obj.users_table.setColumnCount(len(texts.TABLE_COLS['users'][ui_obj.language]))
#     ui_obj.users_table.setHorizontalHeaderLabels(texts.TABLE_COLS['users'][ui_obj.language])


# def get_modify_column_button_widget(ui_obj, disbled=False):
#     """this function is used to get cell widget for modify column in users table
#     """

#     button_delete = QtWidgets.QPushButton()
#     button_delete.setIcon(QtGui.QIcon(REPORTS_DELETE_ICON_PATHES))
#     button_delete.setIconSize(QtCore.QSize(20, 20))
#     button_modify = QtWidgets.QPushButton()
#     button_modify.setIcon(QtGui.QIcon(USERS_MODIFY_ICON_PATH))
#     button_modify.setIconSize(QtCore.QSize(20, 20))
        
#     button_layout = QtWidgets.QHBoxLayout()       
#     button_layout.addWidget(button_delete)
#     button_layout.addWidget(button_modify)
#     button_layout.setContentsMargins(5, 0, 5, 0)
#     button_layout.setSpacing(0)

#     # connect buttons to their functionality
#     button_delete.clicked.connect(partial(lambda: users_delete_record(ui_obj=ui_obj)))
#     button_modify.clicked.connect(partial(lambda: users_edit_record(ui_obj=ui_obj)))

#     # disable buttons if needed
#     if disbled:
#         button_delete.setEnabled(False)
#         button_modify.setEnabled(False)
        
#     buttons_widget = QtWidgets.QWidget()
#     buttons_widget.setLayout(button_layout)

#     return buttons_widget


# def CurrentPos(table_obj):
#     """this function is used to get row and col index of a button clicked in more cell of users table

#     :param table_obj: _description_
#     """

#     clickme = QtWidgets.qApp.focusWidget()
#     index = table_obj.indexAt(clickme.parent().pos())
#     if index.isValid():
#         return index.row(), index.column()


# def set_users_on_table(ui_obj, users_list, start_idx=1):
#     # set num rows
#     ui_obj.users_table.setRowCount(len(users_list))

#     # set vertical indexes
#     ui_obj.users_table.setVerticalHeaderLabels([str(i) for i in range(start_idx, start_idx+ui_obj.users_table.rowCount())])

#     # add records to table
#     for i, item in enumerate(users_list):
#         # username
#         table_item = QtWidgets.QTableWidgetItem(str(item[database.USERS_USERNAME]))
#         table_item.setTextAlignment(QtCore.Qt.AlignCenter)
#         ui_obj.users_table.setItem(i, 1, table_item)

#         # password
#         table_item = QtWidgets.QTableWidgetItem(str(item[database.USERS_PASSWORD]) if item[database.USERS_USERNAME]!=database.DEFAULT_USER_USERNAME else '****')
#         table_item.setTextAlignment(QtCore.Qt.AlignCenter)
#         ui_obj.users_table.setItem(i, 2, table_item)

#         # access level
#         table_item = QtWidgets.QTableWidgetItem(ui_obj.users_access_obj.convert_databse_acess_levels(access_string=str(item[database.USERS_ACCESS_LEVEL])))
#         table_item.setTextAlignment(QtCore.Qt.AlignCenter)
#         ui_obj.users_table.setItem(i, 3, table_item)

#         # modify
#         ui_obj.users_table.setCellWidget(i, 4, get_modify_column_button_widget(ui_obj=ui_obj, disbled=True if item[database.USERS_USERNAME]==database.DEFAULT_USER_USERNAME else False))


# def users_delete_record(ui_obj):
#     """this function is used to delete a user from database, using delete button on table on ui

#     :param api_obj: _description_
#     """

#     # get row index of clicked button
#     row_idx, _ = CurrentPos(table_obj=ui_obj.users_table)

#     # prevent deleting current logined user
#     if ui_obj.login_user_ui.user_info[database.USERS_USERNAME] == ui_obj.users_table.item(row_idx, 1).text():
#         _ = ui_obj.show_alert_window(title=texts.TITLES['delete'][ui_obj.language], message=texts.ERRORS['prevent_delete_user'][ui_obj.language], need_confirm=False)
#         return

#     # confirm delete
#     res = ui_obj.show_alert_window(title=texts.TITLES['delete'][ui_obj.language], message=texts.WARNINGS['delete_user'][ui_obj.language], need_confirm=True)
#     if not res:
#         return

#     # get user info
#     res, _ = ui_obj.users_list_obj.get_user_by_username(username=ui_obj.users_table.item(row_idx, 1).text())
#     if not res:
#         return

#     # delete report in databse
#     res = ui_obj.users_list_obj.delete_user(user_name=ui_obj.users_table.item(row_idx, 1).text())
#     #
#     ui_obj.get_users_items(refresh_table=True)
#     ui_obj.show_alert_window(title=texts.TITLES['delete'][ui_obj.language], message=texts.MESSEGES['db_delete_user'][ui_obj.language], need_confirm=False)


# def users_edit_record(ui_obj):
#     """this function is used to load user info on ui filed to edit

#     :param api_obj: _description_
#     :return: _description_
#     """

#     # get row index of clicked button
#     row_idx, _ = CurrentPos(table_obj=ui_obj.users_table)

#     # prevent deleting current logined user
#     if ui_obj.login_user_ui.user_info[database.USERS_USERNAME] == ui_obj.users_table.item(row_idx, 1).text():
#         _ = ui_obj.show_alert_window(title=texts.TITLES['delete'][ui_obj.language], message=texts.ERRORS['prevent_modify_user'][ui_obj.language], need_confirm=False)
#         return

#     # confirm edit
#     res = ui_obj.show_alert_window(title=texts.TITLES['modify'][ui_obj.language], message=texts.WARNINGS['modify_user'][ui_obj.language], need_confirm=True)
#     if not res:
#         return

#     # get user info
#     res, user_info = ui_obj.users_list_obj.get_user_by_username(username=ui_obj.users_table.item(row_idx, 1).text())
#     if not res:
#         return
    
#     # set user infor to modify user ui and open it
#     ui_obj.modify_user_ui.set_user_info_to_ui(user_info=user_info)
#     ui_obj.modify_user_ui.show_win(modify=True)




class Access_levels():
    """this class is used to manage access levels for users
    """

    def __init__(self, ui_obj):
        self.ui_obj = ui_obj
    

    def convert_databse_acess_levels(self, access_string):
        """this function is used to convert access level boolean flags to access name text

        :param reverse: _description_, defaults to False
        """

        access_items = access_string.split(',')

        access_names = ''
        for i, acc_item in enumerate(access_items):
            if acc_item=='1' or acc_item=='True':
                access_names = access_names + texts.TABLE_COLS['access_levels'][self.ui_obj.language][i] + ', '
        
        return access_names[:-2]
    

    def get_access_levels_boolean_list(self, access_string):
        """this function is used to convert access level boolean flag string to boolean list

        :param access_string: _description_
        """

        access_items = access_string.split(',')
        if access_items[0][0] == '[':
            access_items[0] = access_items[0][1:]
        if access_items[-1][-1] == ']':
            access_items[-1] = access_items[-1][:-1]

        print(access_items)

        for i in range(len(access_items)):
            access_items[i] = access_items[i].strip()

        access_levels = []
        for i, acc_item in enumerate(access_items):
            access_levels.append(True if acc_item=='1' or acc_item=='True' else False)
                
        return access_levels
