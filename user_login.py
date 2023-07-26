import sys
from PyQt5 import QtWidgets, uic, QtCore, QtGui
from functools import partial

from backend import texts, colors, database


ui_file_path = 'log_in_new.ui'

class Login_User_Ui(QtWidgets.QMainWindow):
    """this class is used to build class for calibration results UI

    :param QtWidgets: _description_
    """

    def __init__(self, ui_obj):
        """this function is used to laod ui file and build GUI
        """

        super(Login_User_Ui, self).__init__()

        # load ui file
        uic.loadUi('log_in_new.ui', self)
        self.setWindowFlags(QtCore.Qt.WindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint))

        # language
        
        # try:
        #     self.language = self.ui_obj.language
        # except:
        self.language = 'en'
        self.ui_obj = ui_obj

        # login flag
        self.user_logined = False
        self.user_info = None

        #
        # self.users_username_lineedit.setValidator(QtGui.QRegExpValidator(QtCore.QRegExp("[A-Za-z0-9@_]{0,255}"), self))
        # self.users_password_lineedit.setValidator(QtGui.QRegExpValidator(QtCore.QRegExp("[A-Za-z0-9@_]{0,255}"), self))
        self.close_btn.clicked.connect(partial(self.close_win))
        self.login_pushButton.clicked.connect(partial((self.authenticate_user)))
        # self.users_add_btn.clicked.connect(partial(self.authenticate_user))

    

    def keyPressEvent(self, qKeyEvent):
        """this function is used to close window by escape or enter event

        :param qKeyEvent: _description_
        """

        # enter key
        if qKeyEvent.key() == QtCore.Qt.Key_Return or QtCore.Qt.Key_Enter: 
            self.authenticate_user()
            
        elif qKeyEvent.key() == QtCore.Qt.Key_Escape: 
            self.close_win()


    

    def button_change_icon(self, button_name, icon_path):
        """this function is used to set an icon to a buttin

        :param button_name: _description_
        :param icon: _description_
        """

        # convert label name to pyqt object if is string
        button = eval('self.%s' % (button_name)) if isinstance(button_name, str) else button_name

        try:
            icon = QtGui.QIcon()
            icon.addPixmap(QtGui.QPixmap(icon_path), QtGui.QIcon.Normal, QtGui.QIcon.On)
            button.setIcon(icon)

        except Exception as e:
            self.ui_obj.logger.create_new_log(message=texts.ERRORS['button_set_icon_failed']['en'], level=5)

    
    def show_win(self):
        """this function disables main ui and shows this ui
        """

        # disable main ui
        # try:
        #     self.ui_obj.disable_ui()
        # except:
        #     pass

        self.users_username_lineedit.setFocus()
        self.show()


    def close_win(self):
        """
        this function closes the window
        Inputs: None
        Returns: None
        """

        # # enable main ui
        # try:
        #     self.ui_obj.disable_ui(enable=True)
        # except:
        #     pass

        # close app window and exit the program
        self.clear_user_info_fields()
        self.close()
    

    def resize_window_to_min_height(self, close_win_after=False):
        """this function is used to minimize window height
        """
        
        self.resize(100, 100)
        if close_win_after:
            self.close_win()
    

    def get_user_info_from_ui(self):
        """this function is used to get user info from ui fields

        :param ui_obj: _description_
        """

        user_info = {}
        user_info[database.USERS_USERNAME] = self.users_username_lineedit.text()
        user_info[database.USERS_PASSWORD] = self.users_password_lineedit.text()
        
        return user_info


    def clear_user_info_fields(self):
        """this function is used to clear all user info fields on ui

        :param ui_obj: _description_
        """

        self.users_username_lineedit.setText('')
        self.users_password_lineedit.setText('')


    def authenticate_user(self):
        """this function is used to autenticate user
        """
        
        # get input info from user
        input_user_info = self.get_user_info_from_ui()

        # empty validation
        if input_user_info[database.USERS_PASSWORD] == '' or input_user_info[database.USERS_USERNAME] == '':
            self.show_message('massage_signin_label', text=texts.WARNINGS['fields_empty'][self.language], level=1)
            return False

        # authenticate
        res, user_info = self.ui_obj.users_list_obj.get_user_by_username(username=input_user_info[database.USERS_USERNAME])
        # print("username: ", input_user_info[database.USERS_USERNAME], res)
        # username
        if not res:
            self.show_message('massage_signin_label', text=texts.ERRORS['user_info_invalid'][self.language], level=2)
            return
        # password
        if user_info[database.USERS_PASSWORD] != input_user_info[database.USERS_PASSWORD]:
            self.show_message('massage_signin_label', text=texts.ERRORS['user_info_invalid'][self.language], level=2)
            # print("password: ",isinstance(user_info[database.USERS_PASSWORD], str), isinstance(input_user_info[database.USERS_PASSWORD], str))
            return
        # # access level
        self.ui_obj.user_accsess_levels = self.ui_obj.users_access_obj.get_access_levels_boolean_list(access_string=user_info[database.USERS_ACCESS_LEVEL])
        # print(self.ui_obj.user_accsess_levels)
        #     self.show_message('massage_signin_label', text=texts.ERRORS['user_doesnt_have_access'][self.language], level=2)
        #     return
        
        # authenticate susessfull
        self.user_logined = True
        self.user_info = input_user_info
        self.show_message('massage_signin_label', text=texts.MESSEGES['user_authenticated'][self.language], level=0, close_win_after=True)
        self.ui_obj.disable_application(disable = False)
        # self.ui_obj.login_label.setText(user_info[database.USERS_USERNAME])


    def logout(self):
        self.user_logined = False
        self.user_info = None
        self.ui_obj.disable_application(disable = True)
        # self.ui_obj.login_label.setText(texts.TITLES['no_user_logged_in'][self.language])
        

    def show_message(self, label_name=None, text='', level=0, clearable=True, close_win_after=False):
        """this function is used to show input message in message label,
         also there is a message level determining the color of label, and a timer to clear meesage after a while

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
            print(e)
            return

        if close_win_after:
            self.close_win()




if __name__ == '__main__':
    # ui_file_path = 'log_in_new.ui'
    app = QtWidgets.QApplication(sys.argv)
    window = Login_User_Ui()
    window.show()
    app.exec_()