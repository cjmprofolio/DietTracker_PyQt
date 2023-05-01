from PyQt6.QtSql import QSqlDatabase, QSqlQuery
from PyQt6.QtWidgets import QLineEdit, QMessageBox
from PyQt6.QtCore import QDate, QRegularExpression
from PyQt6.QtGui import QRegularExpressionValidator
from decouple import config
from typing import Union


class Conn2db:
    def __init__(self, dbname:str):

        # Remove old connection before init new one
        self.rmconn()

        self.db= QSqlDatabase.addDatabase('QPSQL', 'myconnection')
        self.db.setHostName(config('HOSTNAME'))
        self.db.setDatabaseName(dbname)
        self.db.setUserName(config('USERNAME'))
        self.db.setPassword(config('PASSWORD'))
        self.db.setPort(config('PORT', cast= int))
    
    def rmconn(self):
        if QSqlDatabase.contains('myconnection'):
            QSqlDatabase.removeDatabase('myconnection')

    def disconn(self):
        if self.db is not None and self.db.open():
            self.db.close()
        else:
            MsgBox(QMessageBox.Icon.Critical, f'There is an error connecting to db: {self.errormsg()}')
        
    def errormsg(self):
        return self.db.lastError().text()

    def query(self):
        if not self.db.open():
            MsgBox(QMessageBox.Icon.Critical, f'There is an error connecting to db: {self.errormsg()}')
        return QSqlQuery(self.db)

def MsgBox(icon: QMessageBox.Icon= QMessageBox.Icon.Information, text: str= 'ERROR', info: str= ''):
    msgbox= QMessageBox()
    msgbox.setIcon(icon)
    msgbox.setText(text)
    msgbox.setInformativeText(info)
    return msgbox.exec()


def CreateValidator(input: Union[QLineEdit, QDate], _: str ,length: int):
    
    return input.setValidator(QRegularExpressionValidator(QRegularExpression(r'[\w ]{1,'+str(length-1)+'}\w{1}$')))


def CheckValidate(input: list):
    # check all input fields are valid
    error_list= []
    for item in input:
        if not item.hasAcceptableInput():
            print(item.objectName())
            error_list.append(item.objectName())
    # if there is any objectName in error_list then exec QMessageBox else return True
    if error_list:
        MsgBox(text="Some input fields are invalid", info= "Input Error: " + ", ".join(error_list))
    else:
        return True

