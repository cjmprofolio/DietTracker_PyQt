from typing import Union
from PyQt6.QtSql import QSqlQueryModel
from PyQt6.QtCore import QDate, QModelIndex
from PyQt6.QtWidgets import QWidget, QMainWindow, QHeaderView
from DietTrackerWindow import Ui_MainWindow_DietTracker
from UpdateOrAddMealWidget import UpdateOrAddMealWidget
from Utils import Conn2db


class DietTrackerWindow(QMainWindow):
    def __init__(self, login_widget: QWidget,login_user: str, db: Conn2db):
        super().__init__()

        # Setup the ui form from designer
        self.ui= Ui_MainWindow_DietTracker()
        self.ui.setupUi(self)
        self.login_widget= login_widget
        self.login_user= login_user
        self.current_date= QDate.currentDate()
        
        # Connect to db
        self.db= db

        # Set start_date and end_date
        self.ResetParams()

        # set label text
        self.ui.label_welcome.setText(f'Welcome to DietTracker, {login_user} !!')
        self.ui.label_date.setText(self.current_date.toString('yyyy-MM-dd'))

        # connect signal to slot
        # calendar part + middle table view part
        self.ui.calendarWidget.clicked.connect(self.Date2Str)
        self.ui.calendarWidget.clicked.connect(self.ShowRecords)
        self.ui.pushButton_add.clicked.connect(self.UpdateOrAddMeal)
        self.ui.pushButton_delete.clicked.connect(self.DeleteMealButton)
        self.ui.tableView_meal.doubleClicked.connect(self.UpdateOrAddMeal)
        # bottom table view part
        self.ui.comboBox_meal.currentTextChanged.connect(self.ShowAllRecords)
        self.ui.dateEdit_start_date.dateChanged.connect(self.ShowAllRecords)
        self.ui.dateEdit_end_date.dateChanged.connect(self.ShowAllRecords)
        self.ui.lineEdit_food.textChanged.connect(self.ShowAllRecords)
        self.ui.lineEdit_place.textChanged.connect(self.ShowAllRecords)
        self.ui.pushButton_reset.clicked.connect(self.ShowAllRecords)
        self.ui.pushButton_reset.clicked.connect(self.ResetParams)

        # menu part
        self.ui.actionLogout.triggered.connect(self.LogOut)
        
        # set params for meals_all records
        self.params= None
        self.ui.pushButton_reset.click()


        # check the tableview is populated or not and show data in tableview
        # self.populated= None
        # self.ui.tableView_meal.setModel(self.ShowRecords(QDate.currentDate()))
        self.ShowRecords()

        # fellowing lines should be added  for tableview
        self.ui.tableView_meal.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.ui.tableView_meal_all.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        
       

    # log out the current user and open login_widget
    def LogOut(self):
        self.close()
        self.login_widget.show()

    # transform QDate to str and set it to label_date
    def Date2Str(self, date: QDate):
        self.ui.label_date.setText(date.toString('yyyy-MM-dd'))

    # set the QSqlTableModel to tableview and show the meal records
    def ShowRecords(self, date: QDate= QDate.currentDate()):
        
        self.db.open()

        meal_model= QSqlQueryModel()
        query= self.db.query()

        date_str= date.toString('yyyy-MM-dd')
        query.exec(f"WITH rank_table AS \
            (SELECT *, \
                RANK() over(PARTITION BY date >= date_trunc('week', CAST('{date_str}' AS DATE)), \
                date < date_trunc('week', CAST('{date_str}' AS DATE)) + INTERVAL '7 days' ORDER BY calorie DESC) as cal_wk_ranking FROM meals)\
            SELECT meal, food, calorie, cal_wk_ranking, place FROM rank_table WHERE date= '{date_str}'\
                ORDER BY CASE meal WHEN 'Breakfast' THEN 1 WHEN 'Brunch' THEN 2 WHEN 'Lunch' THEN 3\
                    WHEN 'Dessert' THEN 4 WHEN 'Dinner' THEN 5 WHEN 'Mid-night snack' THEN 6 END")

        meal_model.setQuery(query)
        self.ui.tableView_meal.setModel(meal_model)
        self.ui.label_date.setText(date.toString('yyyy-MM-dd'))
        
        self.db.close()


    # Update meal to current/selected date
    def UpdateOrAddMeal(self, index: QModelIndex):

        date= self.ui.calendarWidget.selectedDate()
        params= {'date': date, 'login_user': self.login_user, 'db': self.db}
        self.AddForm = UpdateOrAddMealWidget(main_window= self, index= index, **params) # pass main_window to AddMealWidget
        self.AddForm.show()
        
        
    
    def DeleteMealButton(self):
        model= self.ui.tableView_meal.model()
        rows= set(index.row() for index in self.ui.tableView_meal.selectedIndexes())

        self.db.open()
        
        for row in sorted(rows, reverse=True):
            # get the meal record
            meal= model.data(model.index(row, 0))
            date= self.ui.label_date.text()

            query= self.db.query()
            query.exec(f"DELETE FROM meals WHERE date= '{date}' AND meal= '{meal}'")

        # close the db connection and show the reecords after deleting 
        
        self.db.close()
        self.ShowRecords(self.ui.calendarWidget.selectedDate())


    # reset all parameters 
    def ResetParams(self):
        
        self.ui.dateEdit_start_date.setDate(QDate(self.current_date.year(), self.current_date.month(), 1))
        self.ui.dateEdit_end_date.setDate(self.current_date)
        self.ui.comboBox_meal.setCurrentIndex(0)
        self.ui.lineEdit_food.clear()
        self.ui.lineEdit_place.clear()

    # show all meal records based on filter params
    def ShowAllRecords(self, _: Union[str, QDate]=None):
        
        if self.sender() == self.ui.pushButton_reset:
            params_default= {self.ui.dateEdit_start_date: ['date', ''], self.ui.dateEdit_end_date: ['date', ''], self.ui.comboBox_meal: ['meal', ''], 
            self.ui.lineEdit_food: ['food', ''], self.ui.lineEdit_place:['place', '']}
            self.params= params_default
        elif self.sender() in [self.ui.dateEdit_start_date, self.ui.dateEdit_end_date]:
            self.params[self.sender()][1]= self.sender().date().toString('yyyy-MM-dd')
        elif self.sender() == self.ui.comboBox_meal:
            self.params[self.sender()][1]= self.sender().currentText()
        else:
            self.params[self.sender()][1]= self.sender().text()
        

        query_str= f"SELECT date, meal, food, calorie, place FROM meals WHERE name = '{self.login_user}'"

        for param, value in self.params.items():
            if value[1]:
                if param == self.ui.dateEdit_start_date:
                    query_str += f" and {value[0]} >= '{value[1]}'"
                elif param == self.ui.dateEdit_end_date:
                    query_str += f" and {value[0]} <= '{value[1]}'"
                else:
                    query_str += f" and {value[0]} like '%{value[1]}%'"
        query_str+= " ORDER BY date"
        
                               
        self.db.open()
        query= self.db.query()
        meal_model= QSqlQueryModel()
        query.exec(query_str)
        meal_model.setQuery(query)
        self.ui.tableView_meal_all.setModel(meal_model)
        
        self.db.open()
