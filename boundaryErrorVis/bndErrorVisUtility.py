'''
Date: 2021-09-01 21:45:32
LastEditors: Lei Si
LastEditTime: 2021-10-20 19:48:16
'''
from PyQt5 import QtCore
import vtk
from vtkMeshOpt.utility import valueToRGB_i0
import numpy as np

def normalizeV(_n, max_input, min_input):
        newN = 0
        newN = (_n - min_input) / (max_input - min_input)
        if newN > 1:
            print(newN)
        return newN

from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtChart import QChart, QChartView, QBarSeries, QBarCategoryAxis, QBarSet, QLineSeries
from PyQt5.QtGui import QPainter, QColor, QPen
from PyQt5.QtCore import Qt

class QTChartView:
    def __init__(self, _title = "Example"):
        self.title = _title
        # self.create_bar(_hs)
        # self.create_line(_hs)

    def create_bar(self, _hs):
        categories = [str(v) for v in _hs]

        set0 = QBarSet('Hausdorff Distance')
        set0.setPen(QPen(Qt.NoPen))
        for v in _hs:
            distance = _hs[v]
            set0.append(distance)

        series = QBarSeries()
        series.append(set0)

        chart = QChart()
        chart.addSeries(series)
        # chart.setTitle(self.title)
        chart.setAnimationOptions(QChart.SeriesAnimations)

        
        axis = QBarCategoryAxis()
        axis.append(categories)
        chart.createDefaultAxes()
        chart.setAxisX(axis, series)

        chart.legend().setVisible(True)
        chart.legend().setAlignment(Qt.AlignBottom)

        chartView = QChartView(chart)
        chartView.setRenderHint(QPainter.Antialiasing)
        self.chartView = chartView
        return self.chartView

    def create_line(self, _hs):
        categories = [str(v) for v in _hs]

        series = QLineSeries()
        for i, v in enumerate(_hs):
            distance = _hs[v] * 100
            series.append(i, distance)

        chart = QChart()
        chart.addSeries(series)
        chart.setTitle(self.title)
        chart.setAnimationOptions(QChart.SeriesAnimations)

        
        axis = QBarCategoryAxis()
        axis.append(categories)
        chart.createDefaultAxes()
        chart.setAxisX(axis, series)

        chart.legend().setVisible(True)
        chart.legend().setAlignment(Qt.AlignBottom)

        chartView = QChartView(chart)
        chartView.setRenderHint(QPainter.Antialiasing)

        self.lineView = chartView
        return self.lineView
    
    def create_seq_line(self, _hs, _bnd, _color):
        categories = [str(v) for v in _bnd]

        series = QLineSeries()
        series.setName(self.title)
        for i, v in enumerate(_bnd):
            distance = _hs[v] * 100
            series.append(i, distance)

        pen = QPen()
        pen.setWidth(4)
        qc = QColor(_color[0], _color[1], _color[2])
        # qc.fromRgb(_color[0], _color[1], _color[2])
        pen.setColor(qc)
        # pen.setWidth(5)
        series.setPen(pen)

        chart = QChart()
        chart.addSeries(series)
        # chart.setTitle(self.title)
        chart.setAnimationOptions(QChart.SeriesAnimations)


        axis = QBarCategoryAxis()
        # axis.append(categories) # some data will not be shown in window if we add too many categories 
        chart.createDefaultAxes()
        chart.setAxisX(axis, series)

        chart.legend().setVisible(True)
        chart.legend().setAlignment(Qt.AlignBottom)

        chartView = QChartView(chart)
        chartView.setRenderHint(QPainter.Antialiasing)

        self.lineSeqView = chartView
        return self.lineSeqView
    
def createVTKCellArray(cellList, meshType = "Tri"):
    polygons = vtk.vtkCellArray()
    for cell in cellList:
        if meshType == "Hex":
            polygon = vtk.vtkHexahedron()

            PointNum = len(cell)
            polygon.GetPointIds().SetNumberOfIds(PointNum)
            for i, x in enumerate(cell):
                polygon.GetPointIds().SetId(i,x)
            for i in range(polygon.GetNumberOfFaces()):
                # print(i)
                face = polygon.GetFace(i)
                polygons.InsertNextCell(face)
        else:
            polygon = vtk.vtkPolygon()

            PointNum = len(cell)
            polygon.GetPointIds().SetNumberOfIds(PointNum)
            for i, x in enumerate(cell):
                polygon.GetPointIds().SetId(i,x)
            
            polygons.InsertNextCell(polygon)
                
    return polygons

def createVTKPoints(_points):
    points = vtk.vtkPoints()
    for p in _points:
        points.InsertNextPoint(p)
    return points

def createDataSetMapper(_vtkSource):
    mapper = vtk.vtkDataSetMapper()
    mapper.SetInputData(_vtkSource)
    # mapper.ScalarVisibilityOff()
    mapper.ScalarVisibilityOn()
    mapper.SelectColorArray('pointColors')
    mapper.SetScalarModeToUsePointFieldData()
    mapper.SetColorModeToDirectScalars()
    mapper.SetResolveCoincidentTopologyToPolygonOffset()
    return mapper

def createActor(mapper):
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    # actor.GetProperty().SetColor()
    # actor.GetProperty().SetOpacity(0.4)
    return actor

def cellListToPolygon(v,f, pcolors, meshType = "Tri"):
    vtk_points = createVTKPoints(v)
    vtk_polygons = createVTKCellArray(f, meshType)

    polygonData = vtk.vtkPolyData()
    polygonData.SetPoints(vtk_points)
    polygonData.SetPolys(vtk_polygons)
    if type(pcolors) != type([]):
        polygonData.GetPointData().SetScalars(pcolors)

    return polygonData

def polyDataToActor(polydata):
    mapper = createDataSetMapper(polydata)
    actor = createActor(mapper=mapper)
    
    actor.GetProperty().VertexVisibilityOn()
    # actor.GetProperty().SetLineWidth(3.0)
    # if self.flag3D:
    actor.GetProperty().SetRepresentationToSurface()
    return actor

def polygonToBoundaryActor(polygonData):
    '''
    vtk_filter = vtk.vtkDataSetSurfaceFilter()
    vtk_filter.SetInputData(polygonData)
    vtk_filter.Update()
    vtk_geometry = vtk.vtkFeatureEdges()
    vtk_geometry.SetInputConnection(vtk_filter.GetOutputPort())
    # vtk_geometry.SetInputData(polygonData)
    vtk_geometry.BoundaryEdgesOn()
    vtk_geometry.FeatureEdgesOff()
    vtk_geometry.ManifoldEdgesOff()
    vtk_geometry.NonManifoldEdgesOff()
    vtk_geometry.Update()
    '''
    edge_mapper = vtk.vtkPolyDataMapper()
    # edge_mapper.SetInputConnection(vtk_geometry.GetOutputPort())
    edge_mapper.SetInputData(polygonData)
    edge_mapper.ScalarVisibilityOff()

    edge_actor = vtk.vtkActor()
    edge_actor.SetMapper(edge_mapper)
    edge_actor.GetProperty().SetColor(0,0,0)
    # edge_actor.GetProperty().SetLineWidth(30)
    edge_actor.GetProperty().SetRepresentationToWireframe()
    return edge_actor
    
def vfToVTKActor(v, f, pcolors = [], bndFlag = False):
    polydata = cellListToPolygon(v, f, pcolors)
    polyActor = polyDataToActor(polydata)
    if bndFlag:
        pass
        # polyBndActor = polygonToBoundaryActor(polydata)
        # return polyActor, polyBndActor
    return polyActor

def createSphere(in_center, radius):
    # center = [in_center[0] + 0.1 * radius, in_center[1] + 0.1 * radius, in_center[2] + 0.1 * radius]
    center = in_center
    sphereSource = vtk.vtkSphereSource()
    sphereSource.SetRadius(radius)
    sphereSource.SetCenter(center)
    # Make the surface smooth.
    sphereSource.SetPhiResolution(50)
    sphereSource.SetThetaResolution(21)

    mapper = vtk.vtkDataSetMapper()
    mapper.SetInputConnection(sphereSource.GetOutputPort())
    # if use mapper.SetInputData(polygonData.GetOutput())
    # no error and no output

    polyActor = createActor(mapper)

    return polyActor

def pointColors(_v):
    pcolors = vtk.vtkUnsignedCharArray()
    pcolors.SetNumberOfComponents(3)
    pcolors.SetName("pointColors")
    z = _v[:,2]
    max_z = max(z)
    min_z = min(z)
    for i in _v:
        max_z = max(abs(max_z), abs(min_z))
        n = normalizeV(abs(i[2]), max_z, 0)
        if i[2] < 0:
            n = -1 * n
        c = valueToRGB_i0(n) # 1 for blue, when value is [0,1]. 
                                 # -1 for red, when value is [-1, 0].
        c = [int(i * 255) for i in c]
        pcolors.InsertNextTypedTuple(c)
    return pcolors

def pointColorsFromHSDir(_vnumber, _hsDir):
    pcolors = vtk.vtkUnsignedCharArray()
    pcolors.SetNumberOfComponents(3)
    pcolors.SetName("pointColors")
    z = _hsDir.values()
    max_z = max(z)
    min_z = min(z)

    surfaceVertexList = _hsDir.keys()

    max_z = max(abs(max_z), abs(min_z))
    for i in range(_vnumber):
        if i in surfaceVertexList:
            n = normalizeV(abs(_hsDir[i]), max_z, 0)
            if _hsDir[i] < 0:
                n = -1 * n
        else:
            n = 0
        
        c = valueToRGB_i0(n) # 1 for blue, when value is [0,1]. 
                              # -1 for red, when value is [-1, 0].
        c = [int(i * 255) for i in c]
        pcolors.InsertNextTypedTuple(c)
    return pcolors

from QTWindow.webEngineView import webEngineView
from boundaryErrorVis.echartsComponent import *

class QtWebEChartsView:
    def __init__(self, _obj, _title = "Example"):
        self.title = _title
        self.obj = _obj
        # self.create_bar(_hs)
        # self.create_line(_hs)

    def hsToChartFormate(self, _hs, _name):
        dataName = _name
        xlabel = [str(v) for v in _hs.keys()]
        ydata = [100 * x for x in _hs.values()]
        
        y, x = zip(*sorted(zip(ydata, xlabel), reverse = True)) # sort list based on ratios and from big to small.
        ydata = [y]

        return [[dataName], x, ydata]

    def create_bar(self, _hs, _name):
        formatedData = self.hsToChartFormate(_hs, _name)
        htmlName = self.title + ".html"

        chart = echartsBar(htmlName, self.title, formatedData)
        chart.render()

        self.chartView = webEngineView(obj = self.obj)
        htmlUrl = QtCore.QUrl("file://" + chart.fullPath)
        self.chartView.load(htmlUrl)
        # return self.chartView
    
    def bndHsToChartFormat(self, _hs, _bnd):
        names = []
        xarray = list(np.concatenate(_bnd).flat)
        xlabels = [str(x) for x in xarray]
        ydata = []
        for i, v in enumerate(_bnd):
            n = "boundary_" + str(i)
            names.append(n)
            y = [100* _hs[x] if x in v else '-' for x in xarray]
            ydata.append(y)
        return [names, xlabels, ydata]

    def create_seq_bar(self, _hs, _bnd):
        formatedData = self.bndHsToChartFormat(_hs, _bnd)
        htmlName = self.title + ".html"

        chart = echartsBar(htmlName, self.title, formatedData)
        chart.render()

        self.chartView = webEngineView(obj=self.obj)
        htmlUrl = QtCore.QUrl("file://" + chart.fullPath)
        self.chartView.load(htmlUrl)
        # return self.chartView

        