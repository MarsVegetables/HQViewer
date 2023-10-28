'''
Date: 2021-09-02 21:50:53
LastEditors: Lei Si
LastEditTime: 2021-10-20 18:27:43
'''
from QTWindow.bndErrorVisWidgets import bndErrorVisWidgets
from PyQt5 import Qt, QtCore
from PyQt5.QtWidgets import QAction, QDockWidget, QListWidget
from QTWindow.fileSelectWindow import fileSelectWindow

class boundaryErrorWindow(Qt.QMainWindow):
    def __init__(self, parent = None):
        Qt.QMainWindow.__init__(self, parent)
        
        # sshFile="/home/mars/Desktop/Projects/FPCVis/darkorange.stylesheet"

        '''
        sshFile="/home/mars/Desktop/Projects/FPCVis/light.qss"
        '''
        # sshFile=r"F:\UH-PHD\RAProject\FPCVis\light.qss"
        '''
        with open(sshFile,"r",encoding='utf-8') as fh:
            self.setStyleSheet(fh.read())
        '''
        self.filePath = ["",""]
        # layout = QHBoxLayout()
        self.addBar()
        # self.QDockDemo()

        # self.setCentralWidget(QTextEdit()) # should show obj on Central.
        # self.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.items)
        self.setTileAndShowWindow()

    def setModelPath(self, inputPath, pId):
        self.filePath[pId] = inputPath

    def bndVis2D(self):
        bndev = bndErrorVisWidgets(self, self.filePath[0], self.filePath[1], "Quad")
        
        self.centralVTKWidget = bndev.bndOverall2D_vtkWidget()
        self.bndErrorOverallView = bndev.bndErrorOverallHausdorffDisView()
        self.bndErrorChartView = bndev.bndEntireHausdorffDisChartView()

        self.setCentralWidget(self.centralVTKWidget) # should show obj on Central.
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.bndErrorOverallView)
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.bndErrorChartView)

    def bndVis3D(self):
        # print(self.filePath[0], self.filePath[1])
        bndev = bndErrorVisWidgets(self, self.filePath[0], self.filePath[1], "Hex")

        self.centralVTKWidget = bndev.bndOverall3D_vtkWidget()
        self.bndErrorOverallView = bndev.bndErrorOverallHausdorffDisView()
        self.bndErrorChartView = bndev.bndEntireHausdorffDisChartView()
        
        self.setCentralWidget(self.centralVTKWidget) # should show obj on Central.
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.bndErrorOverallView)
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.bndErrorChartView)

    def removeOldWidget(self):
        if hasattr(self, "centralVTKWidget"):
            self.centralVTKWidget.deleteLater()
        if hasattr(self, "bndErrorOverallView"):
            self.bndErrorOverallView.deleteLater()
        if hasattr(self, "bndErrorChartView"):
            self.bndErrorChartView.deleteLater()
    
    def bndVisMain(self, _flag):
        self.removeOldWidget()
        flag_3d = _flag
        if flag_3d:
            self.bndVis3D()
        else:
            self.bndVis2D()

    def setTileAndShowWindow(self, title = "HQView - Boundary Error"):
        ''' Step 1: Initialize the Qt window '''
        self.setWindowTitle(title)
        self.resize(1000,self.height())
        self.show()

    def addBar(self):
        bar = self.menuBar()
        file = bar.addMenu('File')
        openFile = QAction("Open Files", self)
        openFile.triggered.connect(self.openFileEvent)
        file.addAction(openFile)
        resetAction = QAction("Reset", self)
        resetAction.triggered.connect(self.resetEvent)
        file.addAction(resetAction)
        # file.addAction('Quit')

    def openFileEvent(self):
        if hasattr(self, "openEvent"):
            self.openEvent.show()
        else:
            self.openEvent = fileSelectWindow(self)
        if self.openEvent.exec_():
            self.setModelPath(self.openEvent.fileNames[0], 0)
            self.setModelPath(self.openEvent.fileNames[1], 1)
            self.bndVisMain(self.openEvent.flag_3D)
    
    def resetEvent(self):
        self.bndVisMain(self.openEvent.flag_3D)

    def QDockDemo(self):
        self.items = QDockWidget('Dockable', self)

        self.listWidget = QListWidget()
        self.listWidget.addItem("item1")
        self.listWidget.addItem("item2")
        self.listWidget.addItem("item3")
        self.listWidget.addItem("item4")
        
        self.items.setWidget(self.listWidget)
        self.items.setFloating(False)
