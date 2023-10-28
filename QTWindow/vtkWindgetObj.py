'''
Date: 2020-11-07 23:03:57
LastEditors: Lei Si
LastEditTime: 2021-10-19 15:22:08
'''
 
import vtk
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from QTWindow.interactorStyle import KeyPressInteractorPickPoint
from vtkMeshOpt.FPCDisplay import FPCDisplayObj
from vtkMeshOpt.pointOverlappingDet import PointOverlappingDet
from vtkMeshOpt.IntersectDetection import IntersectMarker
from QTWindow.webEngineView import webEngineView
from PyQt5 import QtCore, Qt
from tqdm import tqdm

class windgetDisplayController:
    def __init__(self, frame, file_path, _listwidget, _MaxRadius = 0.1):
        self.fpcObj = FPCDisplayObj(file_path, _MaxRadius)
        self.frame = frame
        self.vtkWidgetObj_main = vtkWindgetObj(self.frame, self.fpcObj, 0, _listwidget)
        self.vtkWidgetObj_sub1 = vtkWindgetObj(self.frame, self.fpcObj, 1, _listwidget)
        self.vtkWidgetObj_sub2 = vtkWindgetObj(self.frame, self.fpcObj, 2, _listwidget)
        self.vtkWindgetList = [self.vtkWidgetObj_main, self.vtkWidgetObj_sub1, self.vtkWidgetObj_sub2]
        # self.vtkWidgetObj_sub3 = vtkWindgetObj(self.frame, self.fpcObj, 3, _listwidget)
        
    def init_vtk_widget_mouseInteractor(self):
        # vtkObjList = [self.vtkWidgetObj_main, self.vtkWidgetObj_sub1, self.vtkWidgetObj_sub2]
        self.MouseInteractorStyle = KeyPressInteractorPickPoint(self, dataset=self.fpcObj.vtkReader.GetOutput())
        self.MouseInteractorStyle1 = KeyPressInteractorPickPoint(self, dataset=self.fpcObj.vtkReader.GetOutput())
        self.MouseInteractorStyle2 = KeyPressInteractorPickPoint(self, dataset=self.fpcObj.vtkReader.GetOutput())

        self.vtkWidgetObj_main.init_vtk_widget(mouseInteractor=True, mouseInteractorStyle=self.MouseInteractorStyle)
        self.vtkWidgetObj_sub1.init_vtk_widget(mouseInteractor=True, mouseInteractorStyle=self.MouseInteractorStyle1)
        self.vtkWidgetObj_sub2.init_vtk_widget(mouseInteractor=True, mouseInteractorStyle=self.MouseInteractorStyle2)
        # self.vtkWidgetObj_sub3.init_vtk_widget()
        # self.vtkWidgetObj_sub3.init_htmlChartView()

    def allQualityChart(self, htmlView):
        ecahrtBarObj = self.fpcObj.allVertexQualityToeChartsBar()
        str_path = ecahrtBarObj.fullPath.replace("\\", "/")
        htmlUrl = QtCore.QUrl("file:///" + str_path)
        # print(htmlUrl)
        htmlView.load(htmlUrl)

    def setCurrentPid(self, _pid):
        self.pid = _pid
    
    def getCurrentPid(self):
        return self.pid
        
class vtkWindgetObj:
    def __init__(self, frame, fpcObj, windowIndex, qtListWidget):
        self.setColors = [[1,1,1], # background
                    [170/255, 110/255, 40/255], # overlapping arrow
                    [1, 0, 1],# intersect polygon
                    [0, 128/255, 0]] # intersect arrow

        self.vtkWidget = QVTKRenderWindowInteractor(frame)
        self.fpcObj = fpcObj
        self.winId = windowIndex
        self.overlappingArrow = PointOverlappingDet(self.fpcObj.generateNpPoints(), self.fpcObj.MaxRadius, self.setColors[1])
        self.IntersectingArrow = IntersectMarker(self.fpcObj.generateNpPoints(), self.fpcObj.cellList, self.fpcObj.MaxRadius, self.setColors[3], self.setColors[2])
        self.qtList = qtListWidget # add overlapping vertex index into QT list widget
        self.indicatorStr = ""
        
        if windowIndex == 2:
            self.init_htmlChartView()

    def init_vtk_widget(self, mouseInteractor = False, mouseInteractorStyle=None):
        self.ren = vtk.vtkRenderer() 
        self.vtkWidget.GetRenderWindow().AddRenderer(self.ren)
        self.vtkWidget.GetRenderWindow().SetMultiSamples(4)
        self.iren = self.vtkWidget.GetRenderWindow().GetInteractor()
        self.mouseInteractorStyle = mouseInteractorStyle

        if mouseInteractor:
            self.addMouseInteractor(self.mouseInteractorStyle)
        # The following set the interactor for 2D image style (i.e., no rotation)
        # style = vtk.vtkInteractorStyleImage()
        # self.iren.SetInteractorStyle(style)
        self.ren.SetBackground(self.setColors[0]) # you can change the background color here

        # Start the vtk screen
        self.ren.ResetCamera()
        # self.show()
        self.iren.Initialize()
        self.iren.Start()
    
    def init_htmlChartView(self):
        if not hasattr(self, "chartView"):
            self.chartView = webEngineView(self)

    def addActorsToRen(self, actors):
        print("adding actors to renderer ...")
        for actor in tqdm(actors):
            self.ren.AddActor(actor)
        self.ren.ResetCamera()
        self.vtkWidget.GetRenderWindow().Render()   
    
    def addMouseInteractor(self, style):
        style.SetDefaultRenderer(self.ren)
        self.vtkWidget.SetInteractorStyle(style)

    def updateIndicatorStr(self, _indicatorStr):
        self.indicatorStr = _indicatorStr
    
    def updateMouseInteractorIndicatorStr(self, _indicatorStr, _bFlag):
        if self.mouseInteractorStyle:
            self.mouseInteractorStyle.indicatorStr = _indicatorStr
            self.mouseInteractorStyle.bFlag = _bFlag

    def displayActor(self, pid=-1, _indicatorStr = "", _bFlag = True):
        self.currentPid = pid # this variable is using in displayCorner()
        _indicatorStr = self.indicatorStr
        self.addOverlappingPointIndexIntoQTList(pid)
        winId = self.winId
        if winId == 0:
            self.displayStarMap(pid, _bFlag = _bFlag)
            if "o" in _indicatorStr:
                self.displayOverlappingArrows()
            else:
                self.removeOverlappingIndicator()
            if "i" in _indicatorStr:
                self.displayIntersectingArrows()
            else:
                self.removeIntersectingIndicator()
        elif winId == 1 and pid >= 0:
            self.displaySubStarMap(pid, _bFlag = _bFlag)
        elif winId == 2 and pid >= 0:
            self.displayMeshPoly(pid)
            self.localElementQualityChart(pid)

    def addOverlappingPointIndexIntoQTList(self, _pid):
        self.qtList.clear()
        if _pid < 0:
            return
        for g in self.overlappingArrow.overlappingGroup:
            if _pid in g:
                # print(g)
                for i in g:
                    self.qtList.addItem(str(i))
                return
        self.qtList.addItem(str(_pid))

    def showBoundaryError(self, _path2):
        self.removeBoundaryError()
        self.bebActor = self.fpcObj.createBoundaryErrorActor(_path2)
        self.addActorsToRen(actors=[self.bebActor])

    def removeBoundaryError(self):
        if hasattr(self, "bebActor"):
            self.removeActors([self.bebActor])

    def removeOverlappingIndicator(self):
        if hasattr(self, "arrowActors"):
            self.removeActors(self.arrowActors)
            
    def displayOverlappingArrows(self):
        if hasattr(self, "arrowActors"):
            self.removeActors(self.arrowActors)

        if hasattr(self, "arrowActors") and (self.fpcObj.MaxRadius == self.overlappingArrow.MaxRadius):
            self.arrowActors = self.overlappingArrow.overlappingArrowActors
        else:
            self.overlappingArrow.updateMaxRadius(self.fpcObj.MaxRadius)
            self.arrowActors = self.overlappingArrow.overlappingPointArrowActions()
        self.addActorsToRen(actors=self.arrowActors)
    
    def removeIntersectingIndicator(self):
        if hasattr(self, "IntersectArrowActors"):
            self.removeActors(self.IntersectArrowActors)
            
    def displayIntersectingArrows(self):
        if hasattr(self, "IntersectArrowActors"):
            self.removeActors(self.IntersectArrowActors)
        
        if hasattr(self, "IntersectArrowActors") and (self.fpcObj.MaxRadius == self.IntersectingArrow.p2a.MaxRadius):
            self.IntersectArrowActors = [self.IntersectingArrow.overlappingCellActor]
            self.IntersectArrowActors.extend(self.IntersectingArrow.arrowActors)
        else:
            self.IntersectingArrow.updateMaxRadius(self.fpcObj.MaxRadius)
            self.IntersectingArrow.run()
            self.IntersectArrowActors = [self.IntersectingArrow.overlappingCellActor]
            self.IntersectArrowActors.extend(self.IntersectingArrow.arrowActors)
        self.addActorsToRen(actors=self.IntersectArrowActors)

    def displayStarMap(self, pid, _bFlag):
        if hasattr(self, "starActors"):
            self.removeActors(self.starActors)
        self.starActors = self.fpcObj.genStarMapActors(selectedPid=pid, _bFlag = _bFlag)
        # self.starActors = self.fpcObj.genStarMapActorsWithoutClusting(selectedPid=pid, _bFlag = _bFlag)
        # self.starActors = self.fpcObj.printAllSector(_bFlag = _bFlag)
        self.addActorsToRen(actors=self.starActors)
    
    def displaySubStarMap(self, pid, _bFlag):
        if hasattr(self, "subStarActors"):
            self.removeActors(self.subStarActors)
        self.subStarActors = self.fpcObj.subStarMapActors(pid, _bFlag = _bFlag)
        self.addActorsToRen(actors=self.subStarActors)
    
    def displayMeshPoly(self, pid):
        if hasattr(self, "cornerActor"):
            self.removeActors(self.cornerActor)
        if hasattr(self, "meshActors"):
            self.removeActors(self.meshActors)
        self.meshActors = self.fpcObj.createConnectionPoly(pid, _sectorFlag = True)
        self.addActorsToRen(actors=self.meshActors)
    
    def localElementQualityChart(self, pid):
        ecahrtBarObj = self.fpcObj.localQualityToeChartsBar(pid)
        htmlUrl = QtCore.QUrl("file://" + ecahrtBarObj.fullPath)
        self.chartView.load(htmlUrl)
        return self.chartView
    
    def displayCorner(self, f):
        if hasattr(self, "cornerActor"):
            self.removeActors(self.cornerActor)
        
        if hasattr(self, "meshActors"):
            self.removeActors(self.meshActors)

        self.meshActors = self.fpcObj.createConnectionPoly(self.currentPid, _sectorFlag = True, _opacity = 0.1)
        self.addActorsToRen(actors=self.meshActors)

        self.cornerActor = self.fpcObj.createCornerActor(f)
        self.addActorsToRen(actors=self.cornerActor)

    def removeActors(self, actors):
        print("removing actors ...")
        for actor in tqdm(actors):
            self.ren.RemoveActor(actor)
        self.ren.ResetCamera()
        self.vtkWidget.GetRenderWindow().Render()   
    

class refVTKWidget:
    def __init__(self, file_path, frame, _MaxRadius) -> None:
        self.fpcObj = FPCDisplayObj(file_path, _MaxRadius)
        self.frame = frame
        self.vtkWidgetObj_main = vtkWindgetObj(self.frame, self.fpcObj, 0, Qt.QListWidget())
        self.MouseInteractorStyle = KeyPressInteractorPickPoint([self.vtkWidgetObj_main], dataset=self.fpcObj.vtkReader.GetOutput())
        self.vtkWidgetObj_main.init_vtk_widget(mouseInteractor=True, mouseInteractorStyle=self.MouseInteractorStyle)
        self.vtkWidget = self.vtkWidgetObj_main.vtkWidget
