'''
Date: 2021-07-06 23:59:42
LastEditors: Lei Si
LastEditTime: 2021-07-08 01:56:53
'''

import vtk
# from vtkMeshOpt.MeshLoader import MeshLoader
# from vtkMeshOpt.utility import valueToRGB
# from vtkMeshOpt.quadMetric import Quad_ScaledJacobian
import math
import numpy as np
from tqdm import tqdm

class overlappingPointCircle:
    def __init__(self, center=np.array((0,0,0)), _maxRadius = 1):
        self.maxRadius = _maxRadius
        self.center = center # (0,0,0)

    def run(self, _num):
        actors = []
        for i in range(_num):
            ratio = i / 10
            radii = ratio * self.maxRadius
            actor = self.createCircle(radii)
            actors.append(actor)
        return actors

    def createCircle(self, _radius):
        polygonSource = vtk.vtkRegularPolygonSource()
        # Comment this line to generate a disk instead of a circle.
        polygonSource.GeneratePolygonOff()
        polygonSource.SetNumberOfSides(50)
        polygonSource.SetRadius(_radius)
        polygonSource.SetCenter(self.center)

        mapper = self.createMapperUseConnection(polygonSource.GetOutputPort())
        actor = self.createActor(mapper)
        return actor
    
    def createMapperUseConnection(self, polydata):
        polyMapper = vtk.vtkPolyDataMapper()
        polyMapper.SetInputConnection(polydata)
        polyMapper.ScalarVisibilityOff()
        return polyMapper
    
    def createActor(self, mapper):
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().EdgeVisibilityOn()
        actor.GetProperty().SetLineWidth(1.0)
        actor.GetProperty().SetColor([255, 0, 0])
        return actor

class overlappingEdgeMarker:

    def __init__(self, center=np.array((0,0,0)), point1=np.array((1,0,0)), _maxRadius = 1):
        self.maxRadius = _maxRadius
        self.center = center # (0,0,0)
        self.point1 = point1 # (1,0,0)

    def updateMaxRadius(self, _maxRadius):
        self.maxRadius = _maxRadius

    def showLine(self):
        line_1 = [self.center, self.point1]
        lineActor_1 = self.drawLine(line_1)
        return lineActor_1

    def lineDirection(self):
        vector_t = self.point1 - self.center
        length = np.sqrt(np.sum(vector_t ** 2))
        if length != 0:
            return vector_t / length
        
    def createOverlappingLineActor(self, _inputRatio):
        normal = self.lineDirection()
        self.barRadii = _inputRatio * self.maxRadius
        barMid = normal * self.barRadii + self.point1
        barTop = self.createBarTop(barMid, normal)
        lineActor = self.drawLine(barTop)
        return lineActor
    
    def createBarTop(self, _barMid, _normal):
        # so far only working on 2D.
        barHalfLen = self.barRadii * 0.5
        if _normal[2] != 0:
            print("Error : current method could not work on 3D model.")
        verticalDirection = np.array([-1 * _normal[1], _normal[0], _normal[2]])
        barP1 = verticalDirection * barHalfLen + _barMid
        barP2 = -1 * verticalDirection * barHalfLen + _barMid
        return [barP1, barP2]
    
    def createMapperUseData(self, polydata):
        polyMapper = vtk.vtkDataSetMapper()
        polyMapper.SetInputData(polydata)
        polyMapper.ScalarVisibilityOff()
        return polyMapper
    
    def createActor(self, mapper):
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().EdgeVisibilityOn()
        actor.GetProperty().SetLineWidth(1.0)
        actor.GetProperty().SetColor([255, 0, 0])
        return actor
    
    def createLineArray(self, PointNum):
        polygon = vtk.vtkLine()
        polygon.GetPointIds().SetNumberOfIds(PointNum)
        for x in range(PointNum):
            polygon.GetPointIds().SetId(x,x)
        
        polygons = vtk.vtkCellArray()
        polygons.InsertNextCell(polygon)
        return polygons

    def createPoints(self, _barPoints):
        points = vtk.vtkPoints()
        for p in _barPoints:
            points.InsertNextPoint(p)
        # points.InsertNextPoint(0.0, 2.0, 0.0)
        return points

    def drawLine(self, _barTop):
        points = self.createPoints(_barTop)
        pointNum = len(_barTop)
        polygons = self.createLineArray(pointNum)

        polygonData = vtk.vtkPolyData()
        polygonData.SetPoints(points)
        polygonData.SetLines(polygons)

        mapper = self.createMapperUseData(polygonData)
        actor = self.createActor(mapper)
        return actor
    
    def run(self, barNum):
        actors = []
        for i in range(barNum):
            ratio = i / 10
            line = self.createOverlappingLineActor(ratio)
            actors.append(line)
        return actors

def test():

    barTopLine = overlappingEdgeMarker(center=np.array((0,0,0)), point1=np.array((1,0,0)), _maxRadius = 1)

    barTopLineActors = barTopLine.run(3)
    angleActors = [barTopLine.showLine()]

    pointCircle = overlappingPointCircle(center=np.array((0,0,0)))
    pcActors = pointCircle.run(3)

    renderer = vtk.vtkRenderer()
    
    # renderer.AddActor(actor)
    for a in barTopLineActors:
        renderer.AddActor(a)
    for a in pcActors:
        renderer.AddActor(a)
    for a in angleActors:
        a.GetProperty().SetColor([1, 0, 0])
        renderer.AddActor(a)

    renderWindow = vtk.vtkRenderWindow()
    renderWindow.AddRenderer(renderer)
    # renderWindow.SetSize(640, 480)

    interactor = vtk.vtkRenderWindowInteractor()
    interactor.SetRenderWindow(renderWindow)

    interactor.Initialize()
    interactor.Start()

# test()