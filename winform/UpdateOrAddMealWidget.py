from typing import Union
from PyQt6.QtCore import QDate, QModelIndex
from PyQt6.QtWidgets import QWidget, QMessageBox, QMainWindow
from UpdateOrAddmealForm import Ui_Form_UpdateOrAddmeal
from Utils import CreateValidator, CheckValidate, MsgBox


class UpdateOrAddMealWidget(QWidget):
    def __init__(self, main_window: QMainWindow, index: QModelIndex, **kwargs):
        super().__init__()
        
        # Setup the ui form from designer
        self.ui= Ui_Form_UpdateOrAddmeal()
        self.ui.setupUi(self)
        
        # Setup index and main_window where to synchronize the add
        self.main_window= main_window
        self.index= index
        self.date= kwargs['date']
        self.login_user= kwargs['login_user']
        self.db= kwargs['db']

        # pass the date info to lineEdit
        self.ui.dateEdit_date.setDate(self.date)

        # establish setting for update current meal record
        if self.index:
            # Change the windowTitle and pushButtoon name
            self.ui.pushButton_add.setText('Update')
            self.setWindowTitle('Update_meal')
            # Get the current meal record by index
            model= self.main_window.ui.tableView_meal.model()
            row= self.index.row()
            self.ui.dateEdit_date.setReadOnly(True)
            self.ui.comboBox_meal.setCurrentText(model.index(row, 0).data())
            self.ui.comboBox_meal.setEnabled(False)
            self.ui.lineEdit_food.setText(model.index(row, 1).data())
            self.ui.spinBox_calorie.setValue(model.index(row, 2).data())
            self.ui.lineEdit_place.setText(model.index(row, 4).data())
            # Set textChanged and valueChanged to SetButtonText
            self.ui.lineEdit_food.textChanged.connect(self.ButtonSetText)
            self.ui.spinBox_calorie.valueChanged.connect(self.ButtonSetText)
            self.ui.lineEdit_place.textChanged.connect(self.ButtonSetText)
            
        # connect signals to slots
        # pushButton_close has already connect to close() of Form using pyqt designer
        self.ui.pushButton_add.clicked.connect(self.UpdateOrAddMeal)

        # Create validators
        CreateValidator(self.ui.lineEdit_food, str, 20)
        CreateValidator(self.ui.lineEdit_place, str, 50)

    def UpdateOrAddMeal(self):
        # instantiate a connection
        self.db.open()

        query= self.db.query()
        date, meal= self.ui.dateEdit_date.text(), self.ui.comboBox_meal.currentText()

        if not self.index:
            # check if same there is same date and meal already in meals table
            query.exec(f"SELECT * FROM meals WHERE date= '{date}' AND meal= '{meal}'")

            if query.next():
                MsgBox(QMessageBox.Icon.Critical, f'There is already a meal record in db.')
                
        else:
            # delete the current record first
            query.exec(f"DELETE FROM meals WHERE date= '{date}' AND meal= '{meal}'")

        # check the input fields before add to sql table
        if CheckValidate([self.ui.lineEdit_food, self.ui.lineEdit_place]):

            # Add new meal record to the db
            food= self.ui.lineEdit_food.text()
            calorie= self.ui.spinBox_calorie.value()
            place= self.ui.lineEdit_place.text()
            query.exec(f" INSERT INTO meals (name, date, meal, food, calorie, place)\
                VALUES ('{self.login_user}', '{date}', '{meal}', '{food}', {calorie}, '{place}')")
            
        self.db.close()
        self.main_window.ShowRecords(QDate.fromString(self.ui.dateEdit_date.text(), 'yyyy-MM-dd'))
            

        # close the db connection is done by ShowRecords() function

    # change the text on button based on text change
    def ButtonSetText(self, _: Union[int, str]):
            self.ui.pushButton_cancel.setText('Done')
