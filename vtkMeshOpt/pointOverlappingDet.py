'''
Date: 2021-05-08 17:53:47
LastEditors: Lei Si
LastEditTime: 2021-10-19 15:00:14
'''

import vtk
import math
from tqdm import tqdm
from vtkMeshOpt.pointsToArrows import PointsToArrows

# USER_MATRIX = True

class PointOverlappingDet:
    def __init__(self, _coords, _MaxRadius, _actorColor):
        # all the coordinations
        self.coords = _coords
        # self.baceObjActor = _baceObjActor
        self.MaxRadius = _MaxRadius
        self.actorColor = _actorColor
        self.arrorActions = []
        self.p2a = PointsToArrows(self.MaxRadius, _actorColor)
        self.overlappingGroup = []

        # for cluster color
        self.colorPic = 0
        self.colorList = [[255,50,0], [0,50,255], [0,255,50], [50, 0, 255], [255,50,50], [50,255,50]]

        # self.overlappingPointArrowActions()

    def updateMaxRadius(self, _maxR):
        self.MaxRadius = _maxR
        self.p2a.updateMaxRadius(self.MaxRadius)

    def overlappingPointArrowActions(self):
        '''
            return arrowAction list
        '''
        print("build overlapping vertex actions ...")
        pointIndex = list(range(len(self.coords)))
        overlappingPoints = []

        pbar = tqdm(total = len(pointIndex))

        self.overlappingGroup = []
        while(len(pointIndex) > 0):
            pointIndex, newArrowEnd, overlappingSubGroup = self.overlappingDet(pointIndex=pointIndex)
            if len(overlappingSubGroup) > 1:
                self.overlappingGroup.append(overlappingSubGroup)
            if newArrowEnd[0][1] > 1:
                overlappingPoints.extend(newArrowEnd)
            pbar.update(len(newArrowEnd))
        endPoints = self.p2a.pointsToArrowEnds(overlappingPoints)
        self.overlappingArrowActors = self.p2a.pointsToArrowAction(endPoints)
        return self.overlappingArrowActors 

    def overlappingDet(self, pointIndex):
        passedIndex = []
        overlappingPoints = []

        i = pointIndex[0]
        p1 = self.coords[i]
        for j in pointIndex:
            p2 = self.coords[j]
            d = self.p2pDistance(p1, p2)
            # overlapping condition
            if d != 0:
                continue
            passedIndex.append(j)
            
        overlappingPoints.append([p1, len(passedIndex)])
        # print(passedIndex) 
        for i in passedIndex:
            pointIndex.remove(i)
        return pointIndex, overlappingPoints, passedIndex

    def p2pDistance(self, p1, p2):
        # point to point distance
        distanceBetween = 0
        for ind in range(len(p1)):
            distanceBetween = distanceBetween + (p1[ind] - p2[ind]) ** 2
        distanceBetween = math.sqrt(distanceBetween)
        return distanceBetween
    
    # set defult point colors and return the char array
    def pointColors(self):
        # not be used 
        self.pcolors = vtk.vtkUnsignedCharArray()
        self.pcolors.SetNumberOfComponents(3)
        self.pcolors.SetName("pointColors")
        c = [100,100,100]
        for i in range(len(self.sphereDir)):
            self.pcolors.InsertNextTypedTuple(c)
    
    def updatePointColors(self, _plist):
        # not be used 
        self.colorPic = (self.colorPic + 1) % len(self.colorList)
        for pid in _plist:
            self.changeSpecificPointColors(pid)
        
    #change specific point's color based on the pid
    def changeSpecificPointColors(self, _pid):
        # not be used 
        self.pcolors.SetTuple(_pid, self.colorList[self.colorPic])

'''
renderWindow = vtk.vtkRenderWindow()
interactor = vtk.vtkRenderWindowInteractor()
import time

def disPlayTest(arrowActors):
    colors = vtk.vtkNamedColors()

    # Set the background color.
    colors.SetColor('BkgColor', [26, 51, 77, 255])

    # Visualize
    renderer = vtk.vtkRenderer()
    for ac in arrowActors:
        renderer.AddActor(ac)
    renderer.SetBackground(colors.GetColor3d('BkgColor'))

    renderWindow.SetSize(640, 480)
    renderWindow.AddRenderer(renderer)

    interactor.SetRenderWindow(renderWindow)

    renderWindow.Render()
    interactor.Start()

pod = PointOverlappingDet([[1,2,0], [1,2,0], [1,2,0], [1,2,0], [1,2,0]], 0.3, [0,0,0])
ac = pod.overlappingPointArrowActions()
disPlayTest(ac)
'''