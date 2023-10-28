'''
Date: 2021-08-30 03:26:33
LastEditors: Lei Si
LastEditTime: 2021-09-14 22:12:20
'''
import sys
from PyQt5 import Qt
# from PyQt5.QtWidgets import *

from boundaryErrorVis.boundaryVisTest import QTChartTest, test_main
from QTWindow.boundaryVisWindow import boundaryErrorWindow


app = Qt.QApplication(sys.argv)
app.setStyle("plastique")
demo = boundaryErrorWindow() # must use a varibale to hold the QT class
# demo.show()
sys.exit(app.exec_())


# test_main()
# QTChartTest()