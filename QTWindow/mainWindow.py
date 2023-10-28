'''
Date: 2020-11-07 22:01:29
LastEditors: Lei Si
LastEditTime: 2023-04-27 14:04:29
'''
 
import os
from PyQt5.QtWidgets import QDockWidget
from PyQt5 import Qt, QtCore
# from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from QTWindow.vtkWindgetObj import windgetDisplayController, refVTKWidget
from QTWindow.boundaryVisWindow import boundaryErrorWindow
from QTWindow.webEngineView import webEngineView

'''
    The Qt MainWindow class
    A vtk widget and the ui controls will be added to this main window
'''
class MainWindow(Qt.QMainWindow):
    def __init__(self, parent = None):
        Qt.QMainWindow.__init__(self, parent)
        
        
        # sshFile="/home/mars/Desktop/Projects/FPCVis/darkorange.stylesheet"
        sshFile= os.path.join(os.getcwd(), "light.qss")
        # sshFile=r"F:\UH-PHD\RAProject\FPCVis\light.qss"
        with open(sshFile,"r",encoding='utf-8') as fh:
            self.setStyleSheet(fh.read())

        ''' Step 1: Initialize the Qt window '''
        self.setWindowTitle("HQView - Mesh Qaulity Analysis")
        self.resize(1000,self.height())
        self.frame = Qt.QFrame() # Create a main window frame to add ui widgets
        self.mainLayout = Qt.QHBoxLayout()  # Set layout - Lines up widgets horizontally
        # self.viewSplitter = QSplitter(QtCore.Qt.Horizontal)  # Set layout - Lines up widgets horizontally

        self.frame.setLayout(self.mainLayout)
        self.setCentralWidget(self.frame)
        
        self.indicatorStr = ""
        self.basicFlag = True
        self.refVTKWidgets = []
        self.refDocks = []
        
        # add working panel in the main layout
        workPanel = self.wrokingLayout()
        workDock = self.addWidgetToDock(workPanel, "Work Panel")
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, workDock)
        # self.viewSplitter.addWidget(workPanel)
        # self.viewSplitterIndex = 0

        # add window widget to main layout
        # self.mainLayout.addWidget(self.viewSplitter)

        self.show()
    
    def AddViewToLayout(self, filePath):
        # self.deleteWidgetAtQSplitter(self.viewSplitterIndex)
        self.deleteOldWidget()
        newRadius = self.sphere_radius.value()
        self.vtkWindgetCon = windgetDisplayController(self.frame, filePath, self.listw, newRadius / 10.)
        self.vtkWindgetCon.setCurrentPid(-1)
        # control displayed sphere and feature edge.
        sphereThreshold, edgeThreshold = self.get_thresholds()
        self.vtkWindgetCon.fpcObj.ShpereRadiiTh = sphereThreshold
        self.vtkWindgetCon.fpcObj.featureEdgeThreshold = edgeThreshold

        ''' Step 2: Add a vtk widget to the central widget '''
        # As we use QHBoxLayout, the vtk widget will be automatically moved to the left
        self.vtkWidgetObj_main = self.vtkWindgetCon.vtkWidgetObj_main
        self.mainLayout.addWidget(self.vtkWidgetObj_main.vtkWidget)


        if not hasattr(self, "allQualityChartView"):
            self.allQualityChartView = webEngineView(self)
        self.vtkWindgetCon.allQualityChart(self.allQualityChartView)
        self.allQualityBarDock = self.addWidgetToDock(self.allQualityChartView, "Overall Vertex Quality Chart")
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, self.allQualityBarDock)
        # self.viewSplitter.addWidget(self.vtkWidgetObj_main.vtkWidget)
        # self.viewSplitterIndex = 1

        ''' Step 3: Add three sub vtk widget to the central widget '''
        # self.right_iwin_splitter = QSplitter(QtCore.Qt.Vertical) # set layout - lines up the controls vertically

        self.vtkWidgetObj_sub1 = self.vtkWindgetCon.vtkWidgetObj_sub1
        self.sub1Dock = self.addWidgetToDock(self.vtkWidgetObj_sub1.vtkWidget, "Sub-region View")
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.sub1Dock)
        # self.right_iwin_splitter.addWidget(self.vtkWidgetObj_sub1.vtkWidget)

        self.vtkWidgetObj_sub2 = self.vtkWindgetCon.vtkWidgetObj_sub2
        self.sub2Dock = self.addWidgetToDock(self.vtkWidgetObj_sub2.vtkWidget, "Local Element View")
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.sub2Dock)
        # self.right_iwin_splitter.addWidget(self.vtkWidgetObj_sub2.vtkWidget)

        # self.vtkWidgetObj_sub3 = self.vtkWindgetCon.vtkWidgetObj_sub3
        self.sub3Dock = self.addWidgetToDock(self.vtkWidgetObj_sub2.chartView, "Selected Point Quality Chart")
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.sub3Dock)

        # self.right_iwin_splitter.addWidget(self.vtkWidgetObj_sub3.vtkWidget)
        # self.viewSplitter.addWidget(self.right_iwin_splitter)
        # self.viewSplitterIndex = 2

        self.vtkWindgetCon.init_vtk_widget_mouseInteractor()
        self.show()
        # Add an object to the rendering window
        # self.add_vtk_object()

    def deleteOldWidget(self):
        if hasattr(self, "vtkWidgetObj_main"):
            self.vtkWidgetObj_main.vtkWidget.deleteLater()
        if hasattr(self, "sub1Dock"):
            self.sub1Dock.close()
        if hasattr(self, "sub2Dock"):
            self.sub2Dock.close()
        if hasattr(self, "sub3Dock"):
            self.sub3Dock.close()
        if hasattr(self, "allQualityBarDock"):
            self.allQualityBarDock.close()
        if len(self.refDocks) > 0:
            for d in self.refDocks:
                d.close()
        self.refDocks = []
        self.refVTKWidgets = []
        
    def wrokingLayout(self):
        right_working_widget = Qt.QWidget() # create a widget
        right_working_layout = Qt.QVBoxLayout() # set layout - lines up the controls vertically
        self.filePathWidget_1(right_working_layout)
        self.filePathWidget_2(right_working_layout)
        self.fileOpenButton(right_working_layout)
        self.boundaryErrorAndRefButton(right_working_layout)
        right_working_layout.addWidget(self.addSphereCheckBox())
        right_working_layout.addWidget(self.addDoubleSpinBox())
        right_working_layout.addWidget(self.addSphereFilterBox())
        right_working_layout.addWidget(self.addFeatureEdgeFilterBox())
        right_working_layout.addWidget(self.addAggregateCheckBox())
        right_working_layout.addWidget(self.addOverlappingCheckBox())
        right_working_layout.addWidget(self.addIntersectingCheckBox())
        # right_working_layout.addWidget(self.addBoundaryErrorCheckBox())
        right_working_layout.addWidget(self.addListBox())
        right_working_widget.setLayout(right_working_layout) #assign the layout to the widget
        return right_working_widget
    
    def filePathWidget_1(self, _workingLayout):
        ''' Add a textfield ( QLineEdit) to show the file path and the browser button '''
        label = Qt.QLabel("Choose file #1 (e.g., vtk):")
        _workingLayout.addWidget(label)
        hbox = Qt.QHBoxLayout()
        self.qt_file_name = Qt.QLineEdit()
        hbox.addWidget(self.qt_file_name) 
        self.qt_browser_button = Qt.QPushButton('Browser')
        self.qt_browser_button.clicked.connect(self.on_file_browser_clicked)
        # self.qt_browser_button.show()
        hbox.addWidget(self.qt_browser_button)
        file_widget = Qt.QWidget()
        file_widget.setLayout(hbox)
        _workingLayout.addWidget(file_widget)
    
    def on_file_browser_clicked(self):
        dlg = Qt.QFileDialog()
        dlg.setFileMode(Qt.QFileDialog.AnyFile)
        dlg.setNameFilter("loadable files (*.vtk)")
        
        if dlg.exec_():
            filenames = dlg.selectedFiles()
            self.qt_file_name.setText(filenames[0])

    def filePathWidget_2(self, _workingLayout):
        ''' Add a textfield ( QLineEdit) to show the file path and the browser button '''
        label = Qt.QLabel("Choose file #2 (e.g., vtk):")
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
        dlg.setNameFilter("loadable files (*.vtk *.mhd *.mesh)")
        
        if dlg.exec_():
            filenames = dlg.selectedFiles()
            self.qt_file_name_2.setText(filenames[0])

    def fileOpenButton(self, _workingLayout):
        fileOpen_widget = Qt.QWidget()
        fileOpen_layout = Qt.QHBoxLayout() #lines up the controls vertically

        self.first_radio = Qt.QRadioButton("File #1")
        self.first_radio.setChecked(True)
        self.openFileNumber = 0
        self.first_radio.toggled.connect(self.on_openFile_radio)
        fileOpen_layout.addWidget(self.first_radio)

        self.second_radio = Qt.QRadioButton("File #2")
        self.second_radio.setChecked(False)
        self.second_radio.toggled.connect(self.on_openFile_radio)
        fileOpen_layout.addWidget(self.second_radio)

        ''' Add the Open button'''
        self.qt_open_button = Qt.QPushButton('Open')
        self.qt_open_button.clicked.connect(self.open_vtk_file)
        fileOpen_layout.addWidget(self.qt_open_button)
        fileOpen_widget.setLayout(fileOpen_layout)
        # self.qt_open_button.show()
        _workingLayout.addWidget(fileOpen_widget)
    
    def boundaryErrorAndRefButton(self, _workingLayout):
        # fnc_widget = Qt.QWidget()
        # fnc_layout = Qt.QHBoxLayout() #lines up the controls vertically

        ''' Add the ref button'''
        self.ref_button = Qt.QPushButton('Open Reference File')
        self.ref_button.clicked.connect(self.open_ref)
        _workingLayout.addWidget(self.ref_button)

        ''' Add the boundary button'''
        self.boundaryError_button = Qt.QPushButton('Boundary Error Analysis')
        self.boundaryError_button.clicked.connect(self.open_boundary_error)
        _workingLayout.addWidget(self.boundaryError_button)

        # fnc_widget.setLayout(fnc_layout)
        # self.qt_open_button.show()
        # _workingLayout.addWidget(fnc_widget)

    def open_boundary_error(self):
        self.bndErrorWindow = boundaryErrorWindow(self)
        self.bndErrorWindow.show()

    def open_ref(self):
        dlg = Qt.QFileDialog()
        dlg.setFileMode(Qt.QFileDialog.AnyFile)
        dlg.setNameFilter("loadable files (*.vtk)")
        
        if dlg.exec_():
            filenames = dlg.selectedFiles()
            print(filenames)
            newRadius = self.sphere_radius.value()
            refwidgetObj = refVTKWidget(filenames[0], self.frame, newRadius / 10.0)
            # control displayed sphere and feature edge.
            sphereThreshold, edgeThreshold = self.get_thresholds()
            refwidgetObj.fpcObj.ShpereRadiiTh = sphereThreshold
            refwidgetObj.fpcObj.featureEdgeThreshold = edgeThreshold
            
            self.refVTKWidgets.append(refwidgetObj)
            refDock = self.addWidgetToDock(refwidgetObj.vtkWidget, "reference file - " + str(len(self.refVTKWidgets)))
            self.refDocks.append(refDock)
            self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, refDock)
            refwidgetObj.vtkWidgetObj_main.updateIndicatorStr(self.indicatorStr)
            refwidgetObj.vtkWidgetObj_main.updateMouseInteractorIndicatorStr(self.indicatorStr, _bFlag = self.basicFlag)
            refwidgetObj.vtkWidgetObj_main.displayActor(_bFlag = self.basicFlag)

            
    def open_vtk_file(self):
        if self.openFileNumber == 0:
            filePath = self.qt_file_name.text()
            self.currentFile = 0
        elif self.openFileNumber == 1:
            filePath = self.qt_file_name_2.text()
            self.currentFile = 1
        self.AddViewToLayout(filePath)
        self.displayViewActor()
        self.setCheckBoxesUnchecked()

    def on_openFile_radio(self):
        if self.first_radio.isChecked() == True:
            self.second_radio.setChecked(False)
            self.openFileNumber = 0
        elif self.second_radio.isChecked() ==  True:
            self.first_radio.setChecked(False)
            self.openFileNumber = 1
    
    def addSphereCheckBox(self):
        groupBox_widget = Qt.QWidget()
        groupBox_layout = Qt.QHBoxLayout()
        self.SphereCheckBox = Qt.QCheckBox("Quality Indicator")
        self.SphereCheckBox.stateChanged.connect(self.onQualityClicked)  
        groupBox_layout.addWidget(self.SphereCheckBox)
        groupBox_widget.setLayout(groupBox_layout)
        return groupBox_widget

    def addAggregateCheckBox(self):
        groupBox_widget = Qt.QWidget()
        groupBox_layout = Qt.QHBoxLayout()
        self.aggregateCheckBox = Qt.QCheckBox("Aggregate glyph")
        self.aggregateCheckBox.stateChanged.connect(self.onAggregateClicked)  
        groupBox_layout.addWidget(self.aggregateCheckBox)
        groupBox_widget.setLayout(groupBox_layout)
        return groupBox_widget

    def addOverlappingCheckBox(self):
        groupBox_widget = Qt.QWidget()
        groupBox_layout = Qt.QHBoxLayout()
        self.overlappingBox = Qt.QCheckBox("Overlapping Indicator - ")
        self.overlappingBox.stateChanged.connect(self.onClicked)  
        groupBox_layout.addWidget(self.overlappingBox)

        self.overlappingLabelBox = Qt.QLabel("Arrow Num: 0")
        groupBox_layout.addWidget(self.overlappingLabelBox)
        groupBox_widget.setLayout(groupBox_layout)
        return groupBox_widget

    def addIntersectingCheckBox(self):
        groupBox_widget = Qt.QWidget()
        groupBox_layout = Qt.QHBoxLayout()
        self.IntersectingBox = Qt.QCheckBox("Intersecting Indicator - ")
        self.IntersectingBox.stateChanged.connect(self.on_Intersecting_Clicked) 
        groupBox_layout.addWidget(self.IntersectingBox)

        self.IntersectingLabelBox = Qt.QLabel("Arrow Num: 0")
        groupBox_layout.addWidget(self.IntersectingLabelBox)
        groupBox_widget.setLayout(groupBox_layout)
        return groupBox_widget

    def addBoundaryErrorCheckBox(self):
        self.BoundaryErrorBox = Qt.QCheckBox("Boundary Error - Ribbon bar")
        self.BoundaryErrorBox.stateChanged.connect(self.on_BoundaryError_Clicked)  
        return self.BoundaryErrorBox

    def setCheckBoxesUnchecked(self):
        self.overlappingBox.setChecked(False)
        self.IntersectingBox.setChecked(False)
        # self.BoundaryErrorBox.setChecked(False)
    
    def addDoubleSpinBox(self):
        groupBox_widget = Qt.QWidget()
        groupBox_layout = Qt.QVBoxLayout() #lines up the controls vertically
        label = Qt.QLabel("Update maximum sphere radius (10x):")
        groupBox_layout.addWidget(label)
        # spin box
        hbox_sphere_radius = Qt.QHBoxLayout()
        self.sphere_radius = Qt.QDoubleSpinBox()
         # set the initial values of some parameters
        self.sphere_radius.setValue(1)
        self.sphere_radius.setRange(0, 20000)
        self.sphere_radius.setSingleStep (0.01)
        hbox_sphere_radius.addWidget(self.sphere_radius)
        # button
        self.sphere_radius_button = Qt.QPushButton("Update")
        self.sphere_radius_button.clicked.connect(self.radius_update_clicked)
        self.sphere_radius_button.show()
        hbox_sphere_radius.addWidget(self.sphere_radius_button) 
        shpere_radius_widget = Qt.QWidget()
        shpere_radius_widget.setLayout(hbox_sphere_radius)
        groupBox_layout.addWidget(shpere_radius_widget)
        groupBox_widget.setLayout(groupBox_layout)
        return groupBox_widget
    
    def addSphereFilterBox(self):
        groupBox_widget = Qt.QWidget()
        groupBox_layout = Qt.QVBoxLayout() #lines up the controls vertically
        label = Qt.QLabel("The minimum radii of displayed sphere (10x):")
        groupBox_layout.addWidget(label)
        # spin box
        hbox_sphere_filter = Qt.QHBoxLayout()
        self.sphere_filter = Qt.QDoubleSpinBox()
        # set the initial values of some parameters
        radius = self.sphere_radius.value()
        self.sphere_filter.setValue(0.2 * radius)
        self.sphere_filter.setRange(0, 20000)
        self.sphere_filter.setSingleStep (0.01)
        hbox_sphere_filter.addWidget(self.sphere_filter)
        # button
        self.sphere_filter_button = Qt.QPushButton("Update")
        self.sphere_filter_button.clicked.connect(self.filter_update_clicked)
        self.sphere_filter_button.show()
        hbox_sphere_filter.addWidget(self.sphere_filter_button) 
        shpere_filter_widget = Qt.QWidget()
        shpere_filter_widget.setLayout(hbox_sphere_filter)
        groupBox_layout.addWidget(shpere_filter_widget)
        groupBox_widget.setLayout(groupBox_layout)
        return groupBox_widget

    def addFeatureEdgeFilterBox(self):
        groupBox_widget = Qt.QWidget()
        groupBox_layout = Qt.QVBoxLayout() #lines up the controls vertically
        label = Qt.QLabel("The maximum quality of featuer edge:")
        groupBox_layout.addWidget(label)
        # spin box
        hbox_feature_edge = Qt.QHBoxLayout()
        self.feature_edge_filter = Qt.QDoubleSpinBox()
         # set the initial values of some parameters
        self.feature_edge_filter.setValue(1)
        self.feature_edge_filter.setRange(-1, 1)
        self.feature_edge_filter.setSingleStep (0.01)
        hbox_feature_edge.addWidget(self.feature_edge_filter)
        # button
        self.feature_edge_filter_button = Qt.QPushButton("Update")
        self.feature_edge_filter_button.clicked.connect(self.feature_edge_update_clicked)
        self.feature_edge_filter_button.show()
        hbox_feature_edge.addWidget(self.feature_edge_filter_button) 
        shpere_radius_widget = Qt.QWidget()
        shpere_radius_widget.setLayout(hbox_feature_edge)
        groupBox_layout.addWidget(shpere_radius_widget)
        groupBox_widget.setLayout(groupBox_layout)
        return groupBox_widget

    def addListBox(self):
        groupBox_widget = Qt.QWidget()
        vbox = Qt.QVBoxLayout()

        lbl = Qt.QLabel('Current Overlapping Vertices:')
        # lbl = Qt.QLabel('Current Selecting Vertices:')

        self.listw = Qt.QListWidget(self)

        self.listw.itemDoubleClicked.connect(self.onListClicked)
        vbox.addWidget(lbl)
        vbox.addWidget(self.listw)

        groupBox_widget.setLayout(vbox)
        return groupBox_widget
    
    def onListClicked(self, item):
        pid = int(item.text())
        self.displayViewActor(pid = pid)
        
    def addComboBox(self):
        groupBox_widget = Qt.QWidget()
        vbox = Qt.QVBoxLayout()

        lbl = Qt.QLabel('Current Local Element:')

        combo = Qt.QComboBox(self)

        # combo.activated[str].connect(self.onActivated)
        vbox.addWidget(lbl)
        vbox.addWidget(combo)

        groupBox_widget.setLayout(vbox)
        return groupBox_widget

    def onQualityClicked(self, state):
        if state == QtCore.Qt.Checked:
            self.basicFlag = False
        else:
            self.basicFlag = True
        self.displayViewActor()
        self.updateMouseInteractorINdicatorStr()

        for r in self.refVTKWidgets:
            r.vtkWidgetObj_main.displayActor(_indicatorStr = self.indicatorStr,_bFlag = self.basicFlag)

    def onAggregateClicked(self, state):  
        self.vtkWindgetCon.fpcObj.aggregatedGlyph(state == QtCore.Qt.Checked)
        
        self.displayViewActor()
        self.updateMouseInteractorINdicatorStr()

        for r in self.refVTKWidgets:
            r.fpcObj.aggregatedGlyph(state == QtCore.Qt.Checked)
            r.vtkWidgetObj_main.displayActor(_indicatorStr = self.indicatorStr,_bFlag = self.basicFlag)


    def onClicked(self, state):
        if state == QtCore.Qt.Checked:
            self.indicatorStr = self.indicatorStr + "o"
            self.vtkWidgetObj_main.displayOverlappingArrows()
            arrowNum = 0
            for i in self.vtkWidgetObj_main.overlappingArrow.overlappingGroup:
                arrowNum += len(i)
            self.overlappingLabelBox.setText("Arrow Num: " + str(arrowNum))

            for r in self.refVTKWidgets:
                r.vtkWidgetObj_main.updateIndicatorStr(self.indicatorStr)
                r.vtkWidgetObj_main.displayOverlappingArrows()
        else:
            self.indicatorStr = self.indicatorStr.replace("o", "")
            self.vtkWidgetObj_main.removeOverlappingIndicator()
            self.overlappingLabelBox.setText("Arrow Num: 0")

            for r in self.refVTKWidgets:
                r.vtkWidgetObj_main.updateIndicatorStr(self.indicatorStr)
                r.vtkWidgetObj_main.removeOverlappingIndicator()

        self.updateMouseInteractorINdicatorStr()

    def on_Intersecting_Clicked(self, state):
        if state == QtCore.Qt.Checked:
            self.indicatorStr = self.indicatorStr + "i"
            self.vtkWidgetObj_main.displayIntersectingArrows()
            arrowNum = self.vtkWidgetObj_main.IntersectingArrow.intersectingPointNum
            self.IntersectingLabelBox.setText("Arrow Num: " + str(arrowNum))
            for r in self.refVTKWidgets:
                r.vtkWidgetObj_main.updateIndicatorStr(self.indicatorStr)
                r.vtkWidgetObj_main.displayIntersectingArrows()
        else:
            self.indicatorStr = self.indicatorStr.replace("i", "")
            self.vtkWidgetObj_main.removeIntersectingIndicator()
            self.IntersectingLabelBox.setText("Arrow Num: 0")
            for r in self.refVTKWidgets:
                r.vtkWidgetObj_main.updateIndicatorStr(self.indicatorStr)
                r.vtkWidgetObj_main.removeIntersectingIndicator()
        self.updateMouseInteractorINdicatorStr()

    def updateMouseInteractorINdicatorStr(self):
        self.vtkWidgetObj_main.updateIndicatorStr(self.indicatorStr)
        self.vtkWidgetObj_sub1.updateIndicatorStr(self.indicatorStr)
        self.vtkWidgetObj_sub2.updateIndicatorStr(self.indicatorStr)
        # self.vtkWidgetObj_sub3.updateIndicatorStr(self.indicatorStr)

        self.vtkWidgetObj_main.updateMouseInteractorIndicatorStr(self.indicatorStr, _bFlag = self.basicFlag)
        self.vtkWidgetObj_sub1.updateMouseInteractorIndicatorStr(self.indicatorStr, _bFlag = self.basicFlag)
        self.vtkWidgetObj_sub2.updateMouseInteractorIndicatorStr(self.indicatorStr, _bFlag = self.basicFlag)
        # self.vtkWidgetObj_sub3.updateMouseInteractorIndicatorStr(self.indicatorStr, _bFlag = self.basicFlag)

    def on_BoundaryError_Clicked(self, state):
        if state == QtCore.Qt.Checked:
            path = ""
            if self.currentFile == 0:
                path = self.qt_file_name_2.text()
            if self.currentFile == 1:
                path = self.qt_file_name.text()
            if path != "":
                self.vtkWidgetObj_main.showBoundaryError(path)
        else:
            self.vtkWidgetObj_main.removeBoundaryError()

    def updateRadius(self):
        newRadius = self.sphere_radius.value()
        newRadius = newRadius / 10.
        if self.vtkWindgetCon.fpcObj.MaxRadius == newRadius:
            return 
        self.vtkWindgetCon.fpcObj.updateMaxRadius(newRadius)
        for r in self.refVTKWidgets:
            r.fpcObj.updateMaxRadius(newRadius)
    
    def updateSphereFilterThorshold(self):
        sphereThreshold = self.sphere_filter.value()
        self.vtkWindgetCon.fpcObj.ShpereRadiiTh = sphereThreshold
        for r in self.refVTKWidgets:
            r.fpcObj.ShpereRadiiTh = sphereThreshold
        
    def updateEdgeFilter(self):
        edgeThreshold = self.feature_edge_filter.value()
        self.vtkWindgetCon.fpcObj.featureEdgeThreshold = edgeThreshold
        for r in self.refVTKWidgets:
            r.fpcObj.featureEdgeThreshold = edgeThreshold

    def updateAllInputValue(self):
        self.updateRadius()
        self.updateSphereFilterThorshold()
        self.updateEdgeFilter()

    def radius_update_clicked(self):
        self.displayViewActor()
        for r in self.refVTKWidgets:
            r.vtkWidgetObj_main.displayActor(_indicatorStr = self.indicatorStr,_bFlag = self.basicFlag)
    
    def filter_update_clicked(self):
        self.displayViewActor()
        for r in self.refVTKWidgets:
            r.vtkWidgetObj_main.displayActor(_indicatorStr = self.indicatorStr,_bFlag = self.basicFlag)
    
    def feature_edge_update_clicked(self):
        self.displayViewActor()
        for r in self.refVTKWidgets:
            r.vtkWidgetObj_main.displayActor(_indicatorStr = self.indicatorStr,_bFlag = self.basicFlag)

    def get_thresholds(self):
        sphereThreshold = self.sphere_filter.value()
        edgeThreshold = self.feature_edge_filter.value()
        return sphereThreshold, edgeThreshold

    def displayViewActor(self, pid = -1):
        print("displaying view actors ...")
        self.updateAllInputValue() # updateAll value based on the user new input.
        
        cpid = pid
        if cpid < 0:
            cpid = self.vtkWindgetCon.getCurrentPid()
        else:
            cpid = pid
            self.vtkWindgetCon.setCurrentPid(cpid)

        self.vtkWindgetCon.fpcObj.setAllActorColorBack()

        self.vtkWidgetObj_main.displayActor(pid = cpid, _bFlag = self.basicFlag)
        self.vtkWidgetObj_sub1.displayActor(pid = cpid, _bFlag = self.basicFlag)
        self.vtkWidgetObj_sub2.displayActor(pid = cpid, _bFlag = self.basicFlag)
        # self.vtkWidgetObj_sub3.displayActor(pid = pid, _bFlag = self.basicFlag)
        print("displaying view actors --- done ...")

    def addWidgetToDock(self, widget, title = "example"):
        DockItem = QDockWidget(title, self)
        DockItem.setWidget(widget)
        DockItem.setFloating(False)
        return DockItem