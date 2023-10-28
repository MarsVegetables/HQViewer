'''
Date: 2021-09-05 02:02:16
LastEditors: Lei Si
LastEditTime: 2021-10-22 00:21:53
'''
 
from PyQt5.QtWidgets import *
from PyQt5 import Qt, QtCore

class fileSelectWindow(QDialog):
    def __init__(self, parentwnd):
        super().__init__(parent = parentwnd)
        self.fileNames = ["",""]
        self.setWindowTitle("File Select sub-Window")
        # must set Window Flags to make Child window become a separate window
        # solution:
        # https://stackoverflow.com/questions/56067373/pyqt5-window-not-opening-on-show-when-parent-window-is-specified
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.Window)
        self.addWidgetToWindow()

    def addWidgetToWindow(self):
        self.mainLayout = Qt.QVBoxLayout()  # Set layout - Lines up widgets horizontally

        self.filePathWidget_2(self.mainLayout)
        self.filePathWidget_1(self.mainLayout)
        self.fileTypeButton(self.mainLayout)
        self.conformButtonWidget(self.mainLayout)

        self.setLayout(self.mainLayout)

    def filePathWidget_1(self, _workingLayout):
        ''' Add a textfield ( QLineEdit) to show the file path and the browser button '''
        label = Qt.QLabel("Sample Model - Choose file (e.g., vtk):")
        _workingLayout.addWidget(label)
        hbox = Qt.QHBoxLayout()
        self.qt_file_name = Qt.QLineEdit()
        hbox.addWidget(self.qt_file_name) 
        self.qt_browser_button_1 = Qt.QPushButton('Browser')
        self.qt_browser_button_1.clicked.connect(self.on_file_browser_clicked_1)
        # self.qt_browser_button.show()
        hbox.addWidget(self.qt_browser_button_1)
        file_widget = Qt.QWidget()
        file_widget.setLayout(hbox)
        _workingLayout.addWidget(file_widget)
    
    def on_file_browser_clicked_1(self):
        dlg = Qt.QFileDialog()
        dlg.setFileMode(Qt.QFileDialog.AnyFile)
        dlg.setNameFilter("loadable files (*.vtk)")
        
        if dlg.exec_():
            filenames = dlg.selectedFiles()
            self.qt_file_name.setText(filenames[0])
        
    def filePathWidget_2(self, _workingLayout):
        ''' Add a textfield ( QLineEdit) to show the file path and the browser button '''
        label = Qt.QLabel("Target Model - Choose file (e.g., vtk):")
        _workingLayout.addWidget(label)
        hbox = Qt.QHBoxLayout()
        self.qt_file_name_2 = Qt.QLineEdit()
        hbox.addWidget(self.qt_file_name_2) 
        self.qt_browser_button_2 = Qt.QPushButton('Browser')
        self.qt_browser_button_2.clicked.connect(self.on_file_browser_clicked_2)
        # self.qt_browser_button.show()
        hbox.addWidget(self.qt_browser_button_2)
        file_widget = Qt.QWidget()
        file_widget.setLayout(hbox)
        _workingLayout.addWidget(file_widget)
    
    def on_file_browser_clicked_2(self):
        dlg = Qt.QFileDialog()
        dlg.setFileMode(Qt.QFileDialog.AnyFile)
        dlg.setNameFilter("loadable files (*.vtk)")
        
        if dlg.exec_():
            filenames = dlg.selectedFiles()
            self.qt_file_name_2.setText(filenames[0])
    
    def conformButtonWidget(self, _workingLayout):
        self.qt_browser_button_2 = Qt.QPushButton('Conform')
        self.qt_browser_button_2.clicked.connect(self.on_conform_clicked)
        _workingLayout.addWidget(self.qt_browser_button_2)
    
    def fileTypeButton(self, _workingLayout):
        fileOpen_widget = Qt.QWidget()
        fileOpen_layout = Qt.QHBoxLayout() #lines up the controls vertically

        self.first_radio = Qt.QRadioButton("2D File")
        self.first_radio.setChecked(True)
        self.flag_3D = False
        self.first_radio.toggled.connect(self.on_openFile_radio)
        fileOpen_layout.addWidget(self.first_radio)

        self.second_radio = Qt.QRadioButton("3D File")
        self.second_radio.setChecked(False)
        self.second_radio.toggled.connect(self.on_openFile_radio)
        fileOpen_layout.addWidget(self.second_radio)
        fileOpen_widget.setLayout(fileOpen_layout)
        _workingLayout.addWidget(fileOpen_widget)

    def on_openFile_radio(self):
        if self.first_radio.isChecked() == True:
            self.second_radio.setChecked(False)
            self.flag_3D = False
        elif self.second_radio.isChecked() ==  True:
            self.first_radio.setChecked(False)
            self.flag_3D = True

    def on_conform_clicked(self):
        self.fileNames[0] = self.qt_file_name.text() # sample
        self.fileNames[1] = self.qt_file_name_2.text() # target
        self.accept()