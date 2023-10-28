'''
Date: 2021-09-05 02:02:16
LastEditors: Lei Si
LastEditTime: 2021-10-19 16:55:30
'''
 
from boundaryErrorVis.boundaryErrorVis3D import boundaryErrorVis3D
from boundaryErrorVis.boundaryErrorVis2D import boundaryErrorVis2D
from boundaryErrorVis.bndErrorVisUtility import QtWebEChartsView
from PyQt5 import Qt
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
import vtk
from PyQt5.QtWidgets import QDockWidget, QVBoxLayout
from vtkMeshOpt.MeshLoader import MeshLoader
from meshStructure.meshDS import meshDS
import os

class bndErrorVisWidgets:
    def __init__(self, mainWnd, samplePath, targetPath, meshType = "") -> None:
        self.mainWnd = mainWnd # mother window
        self.meshType = meshType
        if self.meshType == "":
            print("plz set meshType.")
            return 1
        self.defultColors = [[1,1,1]] # you can change the background color here
        self.samplePath = samplePath
        self.targetPath = targetPath
        self.frame = Qt.QFrame()
        self.buildBndObject()
        
    def buildBndObject(self):
        self.sampleModel, self.samepleVTKReader = self.loadMesh(self.samplePath)
        self.targetModel, self.targetVTKReader = self.loadMesh(self.targetPath)
        if self.meshType == "Quad":
            self.bndObj = boundaryErrorVis2D(self.sampleModel, self.samepleVTKReader, self.targetModel, self.targetVTKReader)
        if self.meshType == "Hex":
            self.bndObj = boundaryErrorVis3D(self.sampleModel, self.samepleVTKReader, self.targetModel, self.targetVTKReader)

    def loadMesh(self, fullFilePath):
        filePath = os.path.dirname(fullFilePath) + "/"
        fileName = os.path.basename(fullFilePath)
        basicGraphic = MeshLoader(filePath, fileName)

        points = basicGraphic.generateNpPoints()
        cells = basicGraphic.cellList_vtk2np()

        print("DS start build.....")
        mesh = meshDS(points, cells, self.meshType)
        mesh.addFilePath(fullFilePath)
        mesh.build()
        return mesh, basicGraphic.vtkReader
    
    def bndEntireHausdorffDisChartView(self):
        # both 2D and 3D obj have hausdorffDistances() functions
        # hausdorff Dis is a list
        chartView = QtWebEChartsView(_obj = self, _title = self.meshType + " - All vertices")
        if self.meshType == "Quad":
            bndVidSet = self.bndObj.bndEidSetToVidsSet()
            hs = self.bndObj.pointDisToPercentage()
            chartView.create_seq_bar(hs, bndVidSet)

        if self.meshType == "Hex":
            hs = self.bndObj.bndDistanceObj.distancePercentageDict_HexIds
            chartView.create_bar(hs, "3D Surface")
        
        return self.addWidgetToDock(chartView.chartView, title=chartView.title)
    
    def bndErrorOverallHausdorffDisView(self):
        if self.meshType == "Quad":
            DockItem = self.bndErrorOverall2D_Dock()
        if self.meshType == "Hex":
            DockItem = self.bndErrorOverall3D_Dock()
        return DockItem

    def bndErrorOverall2D_Dock(self):
        charts = self.bndObj.boundaryDistanceQTLineViews()
        vlayout = QVBoxLayout()
        for l in charts:
            vlayout.addWidget(l.lineSeqView)
        chart_widget = Qt.QWidget() # create a widget
        chart_widget.setLayout(vlayout) #assign the layout to the widget
        
        return self.addWidgetToDock(chart_widget, title="2D Boundary Error")
    
    def removeAllActors(self):
        ren = self.ren
        if self.meshType == "Quad":
            for a in self.actors:
                ren.RemoveActor(a)
            if hasattr(self, "targetBnd"):
                for a in self.targetBnd:
                    ren.RemoveActor(a)
        if self.meshType == "Hex":
            for a in self.actors:
                ren.RemoveActor(a)
            if hasattr(self, "targetSur"):
                ren.RemoveActor(self.targetSur)
            if hasattr(self, "selectedPidOnUVActors"):
                uvRen = self.UVvtkWidget.GetRenderWindow().GetRenderers().GetFirstRenderer()
                for a in self.selectedPidOnUVActors:
                    uvRen.RemoveActor(a)
                self.UVvtkWidget.GetRenderWindow().Render()  
        self.vtkWidget.GetRenderWindow().Render()

    def bnd2D_specificPoint_vtkWidget(self, pid):
        self.actors = self.bndObj.bndSetToVTKlines(pid = pid)
        for a in self.actors:
            self.ren.AddActor(a)
        self.targetBnd = self.bndObj.targetBndToVTkActor()
        for a in self.targetBnd:
            self.ren.AddActor(a)
        self.vtkWidget.GetRenderWindow().Render()  

    def bnd3D_specificPoint_vtkWidget(self, pid):
        # set sample hex mesh surface to a low opacity.
        TargetOpacity = 1
        # self.actors[0].GetProperty().SetOpacity(1)

        # selectedSurfaceActor = self.bndObj.pidToSurfaceActor(pid = pid, acolor = "#cc3300")
        selectedSurfaceActor, selectedPidOnUVActors = self.bndObj.pidToPointActor(pid = pid, acolor = "#cc3300")
        selectedSurfaceActor.GetProperty().SetOpacity(0.8)
        
        if len(self.actors) < 2:
            self.actors.append(selectedSurfaceActor)
        else:
            self.actors[1] = selectedSurfaceActor
        for a in self.actors:
            self.ren.AddActor(a)
        # color = #1a53ff
        self.targetSur = self.bndObj.getTargetSurfaceToVTKActor(acolor = "#000000", opacity = TargetOpacity)
        self.ren.AddActor(self.targetSur)
        self.vtkWidget.GetRenderWindow().Render()  

        # mark selected vertex on UV view
        self.selectedPidOnUVActors = selectedPidOnUVActors
        for a in selectedPidOnUVActors:
            uvRen = self.UVvtkWidget.GetRenderWindow().GetRenderers().GetFirstRenderer()
            a.GetProperty().SetOpacity(0.8)
            uvRen.AddActor(a)
            self.UVvtkWidget.GetRenderWindow().Render()  

    def bndOverall2D_vtkWidget(self):
        self.actors = self.bndObj.bndSetToVTKlines()
        
        vtkWidget = QVTKRenderWindowInteractor(self.frame) # Create a main window frame to add ui widgets
        self.ren = vtk.vtkRenderer()
        self.ren.SetBackground(self.defultColors[0]) 
        for a in self.actors:
            self.ren.AddActor(a)
        vtkWidget.GetRenderWindow().AddRenderer(self.ren)
        vtkWidget.GetRenderWindow().Render()  
        vtkWidget.GetRenderWindow().SetMultiSamples(4)

        self.vtkWidget = vtkWidget
        return self.vtkWidget

    def bndErrorOverall3D_Dock(self):
        # vtk distance filter actor
        # actors = [self.bndObj.bndDistanceObj.filterActor]
        # VTK UV view
        actors = self.bndObj.UVHausdorffDisActor()
        
        vtkWidget = QVTKRenderWindowInteractor(self.frame) # Create a main window frame to add ui widgets
        ren = vtk.vtkRenderer()
        for a in actors:
            ren.AddActor(a)
        ren.SetBackground(self.defultColors[0]) 
        vtkWidget.GetRenderWindow().AddRenderer(ren)
        vtkWidget.GetRenderWindow().Render()  

        self.UVvtkWidget = vtkWidget
        return self.addWidgetToDock(self.UVvtkWidget, title="3D UV with Boundary Error")

    def bndOverall3D_vtkWidget(self):
        self.actors = [self.bndObj.surfaceToVTKWeight()]
        # vtkcolor = vtk.vtkNamedColors()
        # rgb = vtkcolor.HTMLColorToRGB("#999999")
        # self.actors[0].GetProperty().SetColor(rgb[0] / 255, rgb[1] / 255, rgb[2] / 255)

        vtkWidget = QVTKRenderWindowInteractor(self.frame) # Create a main window frame to add ui widgets
        self.ren = vtk.vtkRenderer()
        self.ren.AddActor(self.actors[0])
        self.ren.SetBackground(self.defultColors[0]) 
        vtkWidget.GetRenderWindow().AddRenderer(self.ren)
        vtkWidget.GetRenderWindow().Render()  
        vtkWidget.GetRenderWindow().SetMultiSamples(4)
        
        self.vtkWidget = vtkWidget
        return self.vtkWidget

    def addWidgetToDock(self, widget, title = "example"):
        DockItem = QDockWidget(title, self.mainWnd)
        DockItem.setWidget(widget)
        DockItem.setFloating(False)
        return DockItem