import os
import random, string
from werkzeug.security import generate_password_hash
from captcha.image import ImageCaptcha
from PyQt6.QtWidgets import QWidget, QMessageBox
from PyQt6.QtGui import QPixmap
from RegisterForm import Ui_Form_register
from Utils import Conn2db, CreateValidator, CheckValidate, MsgBox


class RegisterWidget(QWidget):
    def __init__(self, login_widget:QWidget, db: Conn2db):
        super().__init__()
        # Setup Ui designed by pyqt6 designer
        self.ui= Ui_Form_register()
        self.ui.setupUi(self)
        
        self.login_widget= login_widget

        # Connect to db
        self.db= db

        # Setup captcha 
        self.SetupCapcha()

        # Connect signal to slot
        self.ui.pushButton_register.clicked.connect(self.SignUp)
        self.ui.pushButton_refresh.clicked.connect(self.SetupCapcha)
        self.ui.lineEdit_username.editingFinished.connect(self.CheckUsername)
        self.ui.lineEdit_password_2.editingFinished.connect(self.ComparePassword)
        self.ui.pushButton_cancel.clicked.connect(self.CancelRegister)

        # Create Validators
        CreateValidator(self.ui.lineEdit_username, str, 50)
        CreateValidator(self.ui.lineEdit_password_1, str, 16)
        CreateValidator(self.ui.lineEdit_password_2, str, 16)


    def CancelRegister(self):
        self.close()
        self.login_widget.show()

    def SignUp(self):
        # first check if captcha is correct
        if not self.ui.lineEdit_captcha.text() == str(self.captcha):
            MsgBox(text="Wrong captcha...")
            self.ui.lineEdit_captcha.clear()
            self.SetupCapcha()

        # check if input field is valid
        else: 
            if CheckValidate([self.ui.lineEdit_username]):
                self.db.open()

                query= self.db.query()
                username= self.ui.lineEdit_username.text()
                password= generate_password_hash(self.ui.lineEdit_password_1.text())
                query.exec(f"INSERT INTO users (username, password) Values ('{username}', '{password}')")
                
                MsgBox(text="You have registered successfully!!!")

                # remove captcha.png and close the RegisterForm
                os.remove('./tmp/captcha.png')
                self.close()

                self.login_widget.show()

                self.db.close()
                 

    # Set captsha and pixmap
    def SetupCapcha(self):
        try:
            os.remove('./tmp/captcha.png')
        except:
            pass
        self.captcha= ''.join(random.choices(string.digits, k= 5))
        self.captcha_img= ImageCaptcha().write(self.captcha, './tmp/captcha.png')
        self.ui.label_captcha_pixmap.setPixmap(QPixmap('./tmp/captcha.png'))

    # check if username already exist
    def CheckUsername(self):
        
        self.db.open()
        
        query= self.db.query()
        username= self.ui.lineEdit_username.text()
        query.exec(f"SELECT * FROM users WHERE username= '{username}'")

        if query.next():
            self.ui.lineEdit_username.clear()
            MsgBox(text="Name is already been used...")

        self.db.close()
        

    # check if two password inputs are identical
    def ComparePassword(self):
        if not self.ui.lineEdit_password_1.text() == self.ui.lineEdit_password_2.text():
            self.ui.lineEdit_password_1.clear()
            self.ui.lineEdit_password_2.clear()
            MsgBox(QMessageBox.Icon.Warning, "Two passwords are not the same. Please enter identical password in two fields")
        