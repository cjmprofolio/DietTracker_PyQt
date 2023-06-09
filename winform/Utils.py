from PyQt6.QtSql import QSqlDatabase, QSqlQuery
from PyQt6.QtWidgets import QLineEdit, QMessageBox
from PyQt6.QtCore import QDate, QRegularExpression
from PyQt6.QtGui import QRegularExpressionValidator
from decouple import config
from typing import Union


class Conn2db:
    def __init__(self, dbname:str, connect_name: str):
        self.db= None
        self.dbname= dbname
        self.current_connect_name= connect_name
        self.connection_names= []
        self.disconect()
        self.connect()
    
    def disconect(self):
        if QSqlDatabase.contains(self.current_connect_name):
                QSqlDatabase.removeDatabase(self.current_connect_name)

    def connect(self):
        if self.current_connect_name not in self.connection_names:
            self.db= QSqlDatabase.addDatabase('QPSQL', self.current_connect_name)
            self.db.setHostName(config('HOSTNAME'))
            self.db.setDatabaseName(self.dbname)
            self.db.setUserName(config('USERNAME'))
            self.db.setPassword(config('PASSWORD'))
            self.db.setPort(config('PORT', cast= int))
            self.connection_names.append(self.current_connect_name)
        else:
            self.disconect()
            MsgBox(QMessageBox.Icon.Critical, f'connection {self.current_connect_name} is still in use')
            self.connect()
            

    def open(self):
        if self.db:
            self.db.open()

    def close(self):
        if self.db and self.db.isOpen():
            self.db.close()
        else:
            MsgBox(QMessageBox.Icon.Critical, f'There is an error connecting to db: {self.errormsg()}')
    
    def query(self):
        if not self.db.isOpen():
            MsgBox(QMessageBox.Icon.Critical, f'There is an error connecting to db: {self.errormsg()}')
        return QSqlQuery(self.db)

    def errormsg(self):
        return self.db.lastError().text()


def MsgBox(icon: QMessageBox.Icon= QMessageBox.Icon.Information, text: str= 'ERROR', info: str= ''):
    msgbox= QMessageBox()
    msgbox.setIcon(icon)
    msgbox.setText(text)
    msgbox.setInformativeText(info)
    return msgbox.exec()


def CreateValidator(input: Union[QLineEdit, QDate], _: str ,length: int):
    
    return input.setValidator(QRegularExpressionValidator(QRegularExpression(r'[\w ]{0,'+str(length-1)+'}\w{1}$')))


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

