'''
Date: 2021-06-05 23:56:58
LastEditors: Lei Si
LastEditTime: 2023-04-26 03:30:17
'''

import numpy as np
import math
import vtk

class PointsToArrows:
    def __init__(self, _MaxRadius, _actorColor):
        # self.baceObjActor = _baceObjActor
        self.MaxRadius = _MaxRadius
        self.actorColor = _actorColor
        self.arrorActions = []

        # for cluster color
        self.colorPic = 0
        self.colorList = [[255,50,0], [0,50,255], [0,255,50], [50, 0, 255], [255,50,50], [50,255,50]]

    def updateMaxRadius(self, _maxR):
        self.MaxRadius = _maxR
        
    def pointsToArrowEnds(self, _overlappingList):
        endPointsList = []
        for ops in _overlappingList:
            p1 = ops[0]
            aNumber = ops[1]
            # aNumber = 1 # always generate just one arrow
            averageDiff = 360 / aNumber

            theta = np.random.randint(0,360, size = 1)
            for i in range(aNumber):
                aTheta = i * averageDiff + theta
                rad = aTheta * math.pi / 180
                arrowDirection = self.thetaToXYZ(rad)
                startPoint = [0] * 3
                for c in range(len(p1)):
                    startPoint[c] = p1[c] + arrowDirection[c]
                endPointsList.append([startPoint, p1])
        return endPointsList

    def pointsToArrowAction(self, _endPointList):
        arrowActions = []
        for endPoints in _endPointList:
            arrowAction = self.createArrow(endPoints[0], endPoints[1])
            arrowActions.append(arrowAction)
        return arrowActions

    def thetaToXYZ(self, theta):
        # use 2d polar coordination system to select a direction
        endX = self.MaxRadius * math.cos(theta)
        endY = self.MaxRadius * math.sin(theta)
        endZ = 0
        return [endX, endY, endZ]
        
    def createArrow(self, _startPoint, _endPoint):
        #
        # source : https://kitware.github.io/vtk-examples/site/Python/GeometricObjects/OrientedArrow/
        #

        arrowSource = vtk.vtkArrowSource()
        startPoint = _startPoint
        endPoint = _endPoint
        
        normalizedX = [0] * 3
        normalizedY = [0] * 3
        normalizedZ = [0] * 3

        vtk.vtkMath.Subtract(endPoint, startPoint, normalizedX)
        length = vtk.vtkMath.Norm(normalizedX)
        vtk.vtkMath.Normalize(normalizedX)

        # Z axis
        arbitray = [1] * 3
        vtk.vtkMath.Cross(normalizedX, arbitray, normalizedZ)
        vtk.vtkMath.Normalize(normalizedZ)

        vtk.vtkMath.Cross(normalizedZ, normalizedX, normalizedY)
        matrix = vtk.vtkMatrix4x4()
        
        matrix.Identity()
        for i in range(0,3):
            matrix.SetElement(i, 0, normalizedX[i])
            matrix.SetElement(i, 1, normalizedY[i])
            matrix.SetElement(i, 2, normalizedZ[i])
        
        # Apply the transforms
        transform = vtk.vtkTransform()
        transform.Translate(startPoint)
        transform.Concatenate(matrix)
        transform.Scale(length, length, length)

        # Transform the polydata
        transformPD = vtk.vtkTransformPolyDataFilter()
        transformPD.SetTransform(transform)
        transformPD.SetInputConnection(arrowSource.GetOutputPort())

        # Create a mapper and actor for the arrow
        mapper = self.createPolyDataConnectionMapper(transformPD)
        actor = self.createActor(mapper=mapper)
        return actor
    
    def createPolyDataConnectionMapper(self, vtkSource):
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(vtkSource.GetOutputPort())
        mapper.ScalarVisibilityOff()
        return mapper
    
    def createActor(self, mapper):
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetColor(self.actorColor)
        actor.GetProperty().SetOpacity(1)
        return actor