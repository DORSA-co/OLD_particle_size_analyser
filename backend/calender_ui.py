
import sys
from PyQt5 import QtWidgets, uic, QtCore, QtGui
from backend import colors


class Calender(QtWidgets.QMainWindow):
    def __init__(self, ui_obj, years=[], is_it_start = True):  #### True start date
        super(Calender, self).__init__()
        uic.loadUi('calender.ui', self)
        self.setWindowFlags(QtCore.Qt.WindowFlags(QtCore.Qt.FramelessWindowHint))
        ###### setup UI
        self.setWindowIcon(QtGui.QIcon('./Icon/icon.png'))
        # self.setupUi(self)
        self.pos_ = self.pos()
        self._old_pos = None
        self.ui_obj = ui_obj
        self.is_it_start = is_it_start
        ###### flags and variables
        self.selected_date = ''
        ###### working buttons and widjets

        ###### default months
        self.months = ["فروردین", "اردیبهشت", "خرداد", "تیر", "مرداد", "شهریور",
        "مهر", "آبان", "آذر", "دی", "بهمن", "اسفند"]
        ##### default years
        self.years = years#["1396", "1397", "1398", "1399", "1400", "1401", "1402", "1403", "1404"]
        self.comboBox_month.addItems(self.months)
        self.comboBox_year.addItems(self.years)

        self.month_index = self.comboBox_month.currentIndex()
        self.month_name = self.comboBox_month.currentText()
        
        self.year_index = self.comboBox_year.currentIndex()
        self.year_name = self.comboBox_year.currentText()

        self.comboBox_month.currentIndexChanged.connect(self.index_changed_month)
        self.comboBox_year.currentIndexChanged.connect(self.index_changed_year)

        ##### prev and next month buttoms
        # self.pushButton_prev.setIcon(QtGui.QIcon('./Icon/prev.png'))
        self.pushButton_prev.clicked.connect(lambda:self.go_prev_month())
        # self.pushButton_next.setIcon(QtGui.QIcon('./Icon/next.png'))
        self.pushButton_next.clicked.connect(lambda:self.go_next_month())
        self.is_it_a_31_day_month()

        ##### close

        self.close_btn.clicked.connect(self.close_app)

        ##### date buttoms
        self.day = 1  #### default
        self.pushButton_31.clicked.connect(lambda:self.show_selected_date(self.month_index, self.year_name, 31))
        self.pushButton_30.clicked.connect(lambda:self.show_selected_date(self.month_index, self.year_name, 30))
        self.pushButton_29.clicked.connect(lambda:self.show_selected_date(self.month_index, self.year_name, 29))
        self.pushButton_28.clicked.connect(lambda:self.show_selected_date(self.month_index, self.year_name, 28))
        self.pushButton_27.clicked.connect(lambda:self.show_selected_date(self.month_index, self.year_name, 27))
        self.pushButton_26.clicked.connect(lambda:self.show_selected_date(self.month_index, self.year_name, 26))
        self.pushButton_25.clicked.connect(lambda:self.show_selected_date(self.month_index, self.year_name, 25))
        self.pushButton_24.clicked.connect(lambda:self.show_selected_date(self.month_index, self.year_name, 24))
        self.pushButton_23.clicked.connect(lambda:self.show_selected_date(self.month_index, self.year_name, 23))
        self.pushButton_22.clicked.connect(lambda:self.show_selected_date(self.month_index, self.year_name, 22))
        self.pushButton_21.clicked.connect(lambda:self.show_selected_date(self.month_index, self.year_name, 21))
        self.pushButton_20.clicked.connect(lambda:self.show_selected_date(self.month_index, self.year_name, 20))
        self.pushButton_19.clicked.connect(lambda:self.show_selected_date(self.month_index, self.year_name, 19))
        self.pushButton_18.clicked.connect(lambda:self.show_selected_date(self.month_index, self.year_name, 18))
        self.pushButton_17.clicked.connect(lambda:self.show_selected_date(self.month_index, self.year_name, 17))
        self.pushButton_16.clicked.connect(lambda:self.show_selected_date(self.month_index, self.year_name, 16))
        self.pushButton_15.clicked.connect(lambda:self.show_selected_date(self.month_index, self.year_name, 15))
        self.pushButton_14.clicked.connect(lambda:self.show_selected_date(self.month_index, self.year_name, 14))
        self.pushButton_13.clicked.connect(lambda:self.show_selected_date(self.month_index, self.year_name, 13))
        self.pushButton_12.clicked.connect(lambda:self.show_selected_date(self.month_index, self.year_name, 12))
        self.pushButton_11.clicked.connect(lambda:self.show_selected_date(self.month_index, self.year_name, 11))
        self.pushButton_10.clicked.connect(lambda:self.show_selected_date(self.month_index, self.year_name, 10))
        self.pushButton_9.clicked.connect(lambda:self.show_selected_date(self.month_index, self.year_name, 9))
        self.pushButton_8.clicked.connect(lambda:self.show_selected_date(self.month_index, self.year_name, 8))
        self.pushButton_7.clicked.connect(lambda:self.show_selected_date(self.month_index, self.year_name, 7))
        self.pushButton_6.clicked.connect(lambda:self.show_selected_date(self.month_index, self.year_name, 6))
        self.pushButton_5.clicked.connect(lambda:self.show_selected_date(self.month_index, self.year_name, 5))
        self.pushButton_4.clicked.connect(lambda:self.show_selected_date(self.month_index, self.year_name, 4))
        self.pushButton_3.clicked.connect(lambda:self.show_selected_date(self.month_index, self.year_name, 3))
        self.pushButton_2.clicked.connect(lambda:self.show_selected_date(self.month_index, self.year_name, 2))
        self.pushButton_1.clicked.connect(lambda:self.show_selected_date(self.month_index, self.year_name, 1))

    ##### 31 day months
    def is_it_a_31_day_month(self):
        if self.month_index in range(6):
            self.pushButton_31.setEnabled(True)
        else:
            self.pushButton_31.setEnabled(False)

    
    ##### go to previous month
    def go_prev_month(self):
        current_month = self.month_index  ##### going back one month
        if current_month != 0:
            self.month_index = current_month - 1
            self.month_name = self.months[current_month - 1]
            self.comboBox_month.setCurrentIndex(current_month - 1)
        else:
            if self.year_index != 0: #### going to previous year
                prev_year = self.year_index - 1
                self.year_index = prev_year
                self.year_name = prev_year
                self.comboBox_year.setCurrentIndex(prev_year)
                self.month_index = 11   
                self.month_name = self.months[11]
                self.comboBox_month.setCurrentIndex(11)
                       
            else:
                self.show_message(label_name='label_selected_date', text='No Data from Previous Year', level=1, clearable=True)
        self.is_it_a_31_day_month()
    
    
    
    ##### go to next month
    def go_next_month(self):
        current_month = self.month_index  ##### going forward one month
        if current_month != 11:
            self.month_index = current_month + 1
            self.month_name = self.months[current_month + 1]
            self.comboBox_month.setCurrentIndex(current_month + 1)
        else:
            if self.year_index != len(self.years)-1:
                prev_year = self.year_index + 1
                self.year_index = prev_year
                self.year_name = prev_year
                self.comboBox_year.setCurrentIndex(prev_year)
                self.month_index = 0   #### going to next year
                self.month_name = self.months[0]
                self.comboBox_month.setCurrentIndex(0)
            
            else:
                self.show_message(label_name='label_selected_date', text='No Data from Next Year', level=1, clearable=True)
        self.is_it_a_31_day_month()


    ##### show date in label  : label_selected_date
    def show_selected_date(self, month_index, year_name, day):
        if month_index != None:
            self.label_selected_date.setText(year_name +"/" + str(month_index+1) + "/"+str(day))##### add day here 
            self.selected_date = year_name +"/" + str(month_index+1) + "/"+str(day)
            if self.is_it_start: #### its start date
                self.ui_obj.label_start_date_report_search.setText(self.selected_date)
            else:
                self.ui_obj.label_end_date_report_search.setText(self.selected_date)
            self.close_app() 
        else:
            self.label_selected_date.setText('')
            self.selected_date = ''
            self.close_app()
        
    ###### select month 
    def index_changed_month(self, index):
        self.month_index = index
        self.month_name = self.months[index]
        # print("month Index changed", self.month_index)
        # print("month name", self.month_name)
        self.is_it_a_31_day_month()

    ###### select year
    def index_changed_year(self, index):
        self.year_index = index
        self.year_name = self.years[index]
        # print("year Index changed", self.year_index)
        # print("year name", self.year_name)


    def close_app(self):
        """
        this function closes the app
        Inputs: None
        Returns: None
        """

        # close app window and exit the program
        self.close()
        # sys.exit()



    def mouseMoveEvent(self, event):
        """mouse move event for moving window

        :param event: _description_
        """

        if self._old_pos is None:
            return

        delta = QtCore.QPoint(event.globalPos() - self._old_pos)
        self.move(self.x() + delta.x(), self.y() + delta.y())
        self._old_pos = event.globalPos()


    def show_message(self, label_name=None, text='', level=0, clearable=True):
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



if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    win = Calender()
    win.show()
    sys.exit(app.exec())
