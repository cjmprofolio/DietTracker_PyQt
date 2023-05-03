import sys, unittest
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtWidgets import QApplication
from PyQt6.QtTest import QTest
from LoginWidget import LoginWidget
from DietTrackerMainWindow import DietTrackerWindow

class LoginTestCase(unittest.TestCase):

    def setUp(self):
        self.app= QApplication(sys.argv)
        self.login_widget= LoginWidget()


    def testLogin(self):
        QTest.keyClicks(self.login_widget.ui.lineEdit_username, 'jiaming')
        QTest.keyClicks(self.login_widget.ui.lineEdit_password, 'jiaming')
        QTest.mouseClick(self.login_widget.ui.pushButton_login, Qt.MouseButton.LeftButton ,delay= 10)


class DietTrackerTestCase(unittest.TestCase):
    
    def setUp(self):
        self.login_test_case = LoginTestCase()
        self.login_test_case.setUp()
        self.diet_tracker = DietTrackerWindow(self.login_test_case, 'jiaming')
    
    def tearDown(self):
        self.login_test_case.tearDown()
    
    def testloginuser(self):
        # print(self.diet_tracker.login_user, self.login_test_case.login_widget.login_user)
        self.assertEqual(self.diet_tracker.login_user, 'jiaming')

    # def testCalendarper(self):
    #     date= QDate(2023,4,1)
    #     self.diet_tracker.ui.calendarWidget.setSelectedDate(date)

    #     self.assertEqual(self.diet_tracker.ui.label_date.text(), date.toString('yyyy-MM-dd'))

if __name__ == '__main__':
    suite= unittest.TestSuite()
    suite.addTests([LoginTestCase(), DietTrackerTestCase()])
    unittest.main(verbosity=2)