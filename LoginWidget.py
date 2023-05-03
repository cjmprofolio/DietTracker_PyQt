import sys
from werkzeug.security import check_password_hash
from PyQt6.QtWidgets import QWidget, QApplication, QMainWindow
from LoginForm import Ui_Form_login
from DietTrackerMainWindow import DietTrackerWindow
from RegisterWidget import RegisterWidget
from Utils import Conn2db


class LoginWidget(QWidget):
    def __init__(self):
        super().__init__()

        # Use Ui_Form_login from LoginForm designed by pyqt6 designer
        self.ui= Ui_Form_login()
        self.ui.setupUi(self)

        # Connect to db
        self.db= Conn2db(dbname='Qtdb', connect_name='myconnection')
        
        # init a login user to None
        self.login_user= None

        # Connect signal to slot
        self.ui.pushButton_login.clicked.connect(self.LoginButton)
        self.ui.pushButton_register.clicked.connect(self.RegieterButton)
        

        # define shortcut
        self.ui.pushButton_login.setShortcut('Return')

        self.show()

    # connect to Qtdb and check if the user is in users table
    def LoginButton(self):

        self.db.open()

        query= self.db.query()
        query.exec(f"SELECT * FROM users WHERE username= '{self.ui.lineEdit_username.text()}'")
        
        # if login user is in user table then jump to DietTrackerWindow
        if query.next():
            pwhash= query.value(1)
            if check_password_hash(pwhash, self.ui.lineEdit_password.text()):
                self.login_user= self.ui.lineEdit_username.text()
                self.main_window= DietTrackerWindow(self, self.login_user, self.db) # pass LoginWidget and login_user to to DietTrackerWindow
                self.close()
                self.main_window.show()
        else:
            self.ui.label_msg.setText('There is wrong with username or password...')
        self.ui.lineEdit_username.clear()
        self.ui.lineEdit_password.clear()
        
        
    
    def RegieterButton(self):
        self.RegisterForm = RegisterWidget(self, self.db) # pass LoginWidget to RegisterWidget
        self.RegisterForm.show()
        self.close()
        
        

if __name__ == '__main__':
    app= QApplication(sys.argv)
    Login= LoginWidget()
    sys.exit(app.exec())
