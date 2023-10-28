'''
Date: 2020-11-07 22:12:58
LastEditors: Lei Si
LastEditTime: 2021-10-19 01:19:40
'''
 
import sys
from PyQt5 import Qt
from QTWindow.mainWindow import MainWindow

if __name__ == "__main__":
    app = Qt.QApplication(sys.argv)
    app.setStyle("plastique")
    window = MainWindow()
    sys.exit(app.exec_())
