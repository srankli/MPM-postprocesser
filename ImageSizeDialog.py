# PyQt5
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

class ImageSizeDialog(QDialog):
    def __init__(self, parent = None, x = 0, y = 0):
        super(ImageSizeDialog, self).__init__(parent)
        self.setWindowTitle("Size of Image")
        self.resize(150, 60)
        self.setModal(True)
        self.x_length = QLineEdit(self)
        self.x_length.setGeometry(QRect(20, 10, 40, 15))
        if x != 0:
            self.x_length.setText("%d" % x)
        self.y_length = QLineEdit(self)
        self.y_length.setGeometry(QRect(90, 10, 40, 15))
        if y != 0:
            self.y_length.setText("%d" % y)
        self.label_x = QLabel(self)
        self.label_x.setGeometry(QRect(10, 10, 15, 15))
        self.label_x.setText("x:")
        self.label_y = QLabel(self)
        self.label_y.setGeometry(QRect(70, 10, 15, 15))
        self.label_y.setText("y:")
        self.pushButton_ok = QPushButton(self)
        self.pushButton_ok.setGeometry(QRect(20, 30, 55, 15))
        self.pushButton_ok.setObjectName("pushButton_ok")
        self.pushButton_ok.setText("OK")
        self.pushButton_ok.clicked.connect(self.accept)
        self.pushButton_cancel = QPushButton(self)
        self.pushButton_cancel.setGeometry(QRect(80, 30, 55, 15))
        self.pushButton_cancel.setObjectName("pushButton_cancel")
        self.pushButton_cancel.setText("Cancel")
        self.pushButton_cancel.clicked.connect(self.reject)
    
    def getXYText(self):
        return self.x_length.text(), self.y_length.text()
